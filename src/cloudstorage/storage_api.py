# Copyright 2012 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

"""Python wrappers for the Google Storage RESTful API."""

import collections
import os
import urllib.parse
from typing import Optional, Dict, Any, List, Deque

from google.cloud import ndb
from google.cloud import storage
from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account

from . import api_utils
from . import common
from . import errors
from . import rest_api

__all__ = ['ReadBuffer', 'StreamingBuffer']


def _get_storage_api(retry_params, account_id=None):
    """Returns storage_api instance for API methods.

    Args:
        retry_params: An instance of api_utils.RetryParams. If none,
         thread's default will be used.
        account_id: Internal-use only.

    Returns:
        A storage_api instance to handle HTTP requests to GCS.
    """
    api = _StorageApi(_StorageApi.full_control_scope,
                      service_account_id=account_id,
                      retry_params=retry_params)
    if common.local_run() and not common.get_access_token():
        api.api_url = common.local_api_url()
    if common.get_access_token():
        api.token = common.get_access_token()
    return api


class _StorageApi(rest_api._RestApi):
    """A simple wrapper for the Google Storage RESTful API.

    WARNING: Do NOT directly use this api. It's an implementation detail
    and is subject to change at any release.
    """

    api_url = 'https://storage.googleapis.com'
    read_only_scope = 'https://www.googleapis.com/auth/devstorage.read_only'
    read_write_scope = 'https://www.googleapis.com/auth/devstorage.read_write'
    full_control_scope = 'https://www.googleapis.com/auth/devstorage.full_control'

    def __getstate__(self):
        """Store state as part of serialization/pickling."""
        return (super(_StorageApi, self).__getstate__(), {'api_url': self.api_url})

    def __setstate__(self, state):
        """Restore state as part of deserialization/unpickling."""
        superstate, localstate = state
        super(_StorageApi, self).__setstate__(superstate)
        self.api_url = localstate['api_url']

    @ndb.tasklet
    def do_request_async(self, url, method='GET', headers=None, payload=None,
                         deadline=None, callback=None):
        """Inherit docs.

        This method translates HTTP exceptions to more service-specific ones.
        """
        if headers is None:
            headers = {}
        if 'x-goog-api-version' not in headers:
            headers['x-goog-api-version'] = '2'
        headers['accept-encoding'] = 'gzip, *'
        try:
            resp_tuple = yield super(_StorageApi, self).do_request_async(
                url, method=method, headers=headers, payload=payload,
                deadline=deadline, callback=callback)
        except Exception as e:
            raise errors.TimeoutError(
                'Request to Google Cloud Storage timed out.', e)

        raise ndb.Return(resp_tuple)

    def post_object_async(self, path, **kwds):
        """POST to an object."""
        return self.do_request_async(self.api_url + path, 'POST', **kwds)

    def put_object_async(self, path, **kwds):
        """PUT an object."""
        return self.do_request_async(self.api_url + path, 'PUT', **kwds)

    def get_object_async(self, path, **kwds):
        """GET an object."""
        return self.do_request_async(self.api_url + path, 'GET', **kwds)

    def delete_object_async(self, path, **kwds):
        """DELETE an object."""
        return self.do_request_async(self.api_url + path, 'DELETE', **kwds)

    def head_object_async(self, path, **kwds):
        """HEAD an object."""
        return self.do_request_async(self.api_url + path, 'HEAD', **kwds)

    def get_bucket_async(self, path, **kwds):
        """GET a bucket."""
        return self.do_request_async(self.api_url + path, 'GET', **kwds)


_StorageApi = rest_api.add_sync_methods(_StorageApi)


class ReadBuffer:
    """A class for reading Google Storage files."""

    DEFAULT_BUFFER_SIZE = 1024 * 1024
    MAX_REQUEST_SIZE = 30 * DEFAULT_BUFFER_SIZE

    def __init__(self, api, path, buffer_size=DEFAULT_BUFFER_SIZE,
                 max_request_size=MAX_REQUEST_SIZE):
        """Constructor.

        Args:
            api: A StorageApi instance.
            path: Quoted/escaped path to the object, e.g. /mybucket/myfile
            buffer_size: buffer size.
            max_request_size: Max bytes to request in one HTTP request.
        """
        self._api = api
        self._path = path
        self.name = api_utils._unquote_filename(path)
        self.closed = False

        assert buffer_size <= max_request_size
        self._buffer_size = buffer_size
        self._max_request_size = max_request_size
        self._offset = 0
        self._buffer = _Buffer()
        self._etag = None

        get_future = self._get_segment(0, self._buffer_size, check_response=False)

        status, headers, content = self._api.head_object(path)
        errors.check_status(status, [200], path, resp_headers=headers, body=content)
        self._file_size = int(common.get_stored_content_length(headers))
        self._check_etag(headers.get('etag'))

        self._buffer_future = None

        if self._file_size != 0:
            content, check_response_closure = get_future.get_result()
            check_response_closure()
            self._buffer.reset(content)
            self._request_next_buffer()

    def __getstate__(self):
        """Store state as part of serialization/pickling."""
        return {'api': self._api,
                'path': self._path,
                'buffer_size': self._buffer_size,
                'request_size': self._max_request_size,
                'etag': self._etag,
                'size': self._file_size,
                'offset': self._offset,
                'closed': self.closed}

    def __setstate__(self, state):
        """Restore state as part of deserialization/unpickling."""
        self._api = state['api']
        self._path = state['path']
        self.name = api_utils._unquote_filename(self._path)
        self._buffer_size = state['buffer_size']
        self._max_request_size = state['request_size']
        self._etag = state['etag']
        self._file_size = state['size']
        self._offset = state['offset']
        self._buffer = _Buffer()
        self.closed = state['closed']
        self._buffer_future = None
        if self._remaining() and not self.closed:
            self._request_next_buffer()

    def __iter__(self):
        """Iterator interface."""
        return self

    def __next__(self):
        line = self.readline()
        if not line:
            raise StopIteration()
        return line

    def readline(self, size=-1):
        """Read one line delimited by '\n' from the file."""
        self._check_open()
        if size == 0 or not self._remaining():
            return ''

        data_list = []
        newline_offset = self._buffer.find_newline(size)
        while newline_offset < 0:
            data = self._buffer.read(size)
            size -= len(data)
            self._offset += len(data)
            data_list.append(data)
            if size == 0 or not self._remaining():
                return ''.join(data_list)
            self._buffer.reset(self._buffer_future.get_result())
            self._request_next_buffer()
            newline_offset = self._buffer.find_newline(size)

        data = self._buffer.read_to_offset(newline_offset + 1)
        self._offset += len(data)
        data_list.append(data)

        return ''.join(data_list)

    def read(self, size=-1):
        """Read data from RAW file."""
        self._check_open()
        if not self._remaining():
            return ''

        data_list = []
        while True:
            remaining = self._buffer.remaining()
            if size >= 0 and size < remaining:
                data_list.append(self._buffer.read(size))
                self._offset += size
                break
            else:
                size -= remaining
                self._offset += remaining
                data_list.append(self._buffer.read())

                if self._buffer_future is None:
                    if size < 0 or size >= self._remaining():
                        needs = self._remaining()
                    else:
                        needs = size
                    data_list.extend(self._get_segments(self._offset, needs))
                    self._offset += needs
                    break

                if self._buffer_future:
                    self._buffer.reset(self._buffer_future.get_result())
                    self._buffer_future = None

        if self._buffer_future is None:
            self._request_next_buffer()
        return ''.join(data_list)

    def _remaining(self):
        return self._file_size - self._offset

    def _request_next_buffer(self):
        """Request next buffer."""
        self._buffer_future = None
        next_offset = self._offset + self._buffer.remaining()
        if next_offset != self._file_size:
            self._buffer_future = self._get_segment(next_offset,
                                                    self._buffer_size)

    def _get_segments(self, start, request_size):
        """Get segments of the file from Google Storage as a list."""
        if not request_size:
            return []

        end = start + request_size
        futures = []

        while request_size > self._max_request_size:
            futures.append(self._get_segment(start, self._max_request_size))
            request_size -= self._max_request_size
            start += self._max_request_size
        if start < end:
            futures.append(self._get_segment(start, end-start))
        return [fut.get_result() for fut in futures]

    @ndb.tasklet
    def _get_segment(self, start, request_size, check_response=True):
        """Get a segment of the file from Google Storage."""
        end = start + request_size - 1
        content_range = '%d-%d' % (start, end)
        headers = {'Range': 'bytes=' + content_range}
        status, resp_headers, content = yield self._api.get_object_async(
            self._path, headers=headers)
        def _checker():
            errors.check_status(status, [200, 206], self._path, headers,
                                resp_headers, body=content)
            self._check_etag(resp_headers.get('etag'))
        if check_response:
            _checker()
            raise ndb.Return(content)
        raise ndb.Return(content, _checker)

    def _check_etag(self, etag):
        """Check if etag is the same across requests to GCS."""
        if etag is None:
            return
        elif self._etag is None:
            self._etag = etag
        elif self._etag != etag:
            raise ValueError('File on GCS has changed while reading.')

    def close(self):
        self.closed = True
        self._buffer = None
        self._buffer_future = None

    def __enter__(self):
        return self

    def __exit__(self, atype, value, traceback):
        self.close()
        return False

    def seek(self, offset, whence=os.SEEK_SET):
        """Set the file's current offset."""
        self._check_open()

        self._buffer.reset()
        self._buffer_future = None

        if whence == os.SEEK_SET:
            self._offset = offset
        elif whence == os.SEEK_CUR:
            self._offset += offset
        elif whence == os.SEEK_END:
            self._offset = self._file_size + offset
        else:
            raise ValueError('Whence mode %s is invalid.' % str(whence))

        self._offset = min(self._offset, self._file_size)
        self._offset = max(self._offset, 0)
        if self._remaining():
            self._request_next_buffer()

    def tell(self):
        """Return the current offset."""
        self._check_open()
        return self._offset

    def _check_open(self):
        if self.closed:
            raise IOError('Buffer is closed.')

    def seekable(self):
        return True

    def readable(self):
        return True

    def writable(self):
        return False


class _Buffer:
    """In-memory buffer."""

    def __init__(self):
        self.reset()

    def reset(self, content='', offset=0):
        self._buffer = content
        self._offset = offset

    def read(self, size=-1):
        """Returns bytes from self._buffer and update related offsets."""
        if size < 0:
            offset = len(self._buffer)
        else:
            offset = self._offset + size
        return self.read_to_offset(offset)

    def read_to_offset(self, offset):
        """Returns bytes from self._buffer and update related offsets."""
        assert offset >= self._offset
        result = self._buffer[self._offset: offset]
        self._offset += len(result)
        return result

    def remaining(self):
        return len(self._buffer) - self._offset

    def find_newline(self, size=-1):
        """Search for newline char in buffer starting from current offset."""
        if size < 0:
            return self._buffer.find('\n', self._offset)
        return self._buffer.find('\n', self._offset, self._offset + size)


class StreamingBuffer:
    """A class for creating large objects using the 'resumable' API."""

    _blocksize = 256 * 1024
    _flushsize = 8 * _blocksize
    _maxrequestsize = 9 * 4 * _blocksize

    def __init__(self, api, path, content_type=None, gcs_headers=None):
        """Constructor."""
        assert self._maxrequestsize > self._blocksize
        assert self._maxrequestsize % self._blocksize == 0
        assert self._maxrequestsize >= self._flushsize

        self._api = api
        self._path = path

        self.name = api_utils._unquote_filename(path)
        self.closed = False

        self._buffer = collections.deque()
        self._buffered = 0
        self._written = 0
        self._offset = 0

        headers = {'x-goog-resumable': 'start'}
        if content_type:
            headers['content-type'] = content_type
        if gcs_headers:
            headers.update(gcs_headers)
        status, resp_headers, content = self._api.post_object(path, headers=headers)
        errors.check_status(status, [201], path, headers, resp_headers,
                            body=content)
        loc = resp_headers.get('location')
        if not loc:
            raise IOError('No location header found in 201 response')
        parsed = urllib.parse.urlparse(loc)
        self._path_with_token = '%s?%s' % (self._path, parsed.query)

    def __getstate__(self):
        """Store state as part of serialization/pickling."""
        return {'api': self._api,
                'path': self._path,
                'path_token': self._path_with_token,
                'buffer': self._buffer,
                'buffered': self._buffered,
                'written': self._written,
                'offset': self._offset,
                'closed': self.closed}

    def __setstate__(self, state):
        """Restore state as part of deserialization/unpickling."""
        self._api = state['api']
        self._path_with_token = state['path_token']
        self._buffer = state['buffer']
        self._buffered = state['buffered']
        self._written = state['written']
        self._offset = state['offset']
        self.closed = state['closed']
        self._path = state['path']
        self.name = api_utils._unquote_filename(self._path)

    def write(self, data):
        """Write some bytes."""
        self._check_open()
        if not isinstance(data, str):
            raise TypeError('Expected str but got %s.' % type(data))
        if not data:
            return
        self._buffer.append(data)
        self._buffered += len(data)
        self._offset += len(data)
        if self._buffered >= self._flushsize:
            self._flush()

    def flush(self):
        """Flush as much as possible to GCS."""
        self._check_open()
        self._flush(finish=False)

    def tell(self):
        """Return the total number of bytes passed to write() so far."""
        return self._offset

    def close(self):
        """Flush the buffer and finalize the file."""
        if not self.closed:
            self.closed = True
            self._flush(finish=True)
            self._buffer = None

    def __enter__(self):
        return self

    def __exit__(self, atype, value, traceback):
        self.close()
        return False

