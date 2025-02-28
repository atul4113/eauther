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

"""Helpers shared by cloudstorage_stub and cloudstorage_api."""

__all__ = [
    'CS_XML_NS',
    'CSFileStat',
    'dt_str_to_posix',
    'local_api_url',
    'LOCAL_GCS_ENDPOINT',
    'local_run',
    'get_access_token',
    'get_stored_content_length',
    'get_metadata',
    'GCSFileStat',
    'http_time_to_posix',
    'memory_usage',
    'posix_time_to_http',
    'posix_to_dt_str',
    'set_access_token',
    'validate_options',
    'validate_bucket_name',
    'validate_bucket_path',
    'validate_file_path',
]

import calendar
import datetime
from email import utils as email_utils
import logging
import os
import re
import sys
from typing import Dict, Optional, Tuple

# Define constants
_GCS_BUCKET_REGEX_BASE = r'[a-z0-9\.\-_]{3,63}'
_GCS_BUCKET_REGEX = re.compile(_GCS_BUCKET_REGEX_BASE + r'$')
_GCS_BUCKET_PATH_REGEX = re.compile(r'/' + _GCS_BUCKET_REGEX_BASE + r'$')
_GCS_PATH_PREFIX_REGEX = re.compile(r'/' + _GCS_BUCKET_REGEX_BASE + r'.*')
_GCS_FULLPATH_REGEX = re.compile(r'/' + _GCS_BUCKET_REGEX_BASE + r'/.*')
_GCS_METADATA = ['x-goog-meta-', 'content-disposition', 'cache-control', 'content-encoding']
_GCS_OPTIONS = _GCS_METADATA + ['x-goog-acl']
CS_XML_NS = 'http://doc.s3.amazonaws.com/2006-03-01'
LOCAL_GCS_ENDPOINT = '/_ah/gcs'
_access_token = ''


def set_access_token(access_token: str) -> None:
    """Set the shared access token to authenticate with Google Cloud Storage.

    Args:
        access_token: The access token to use for authentication.
    """
    global _access_token
    _access_token = access_token


def get_access_token() -> str:
    """Returns the shared access token."""
    return _access_token


class GCSFileStat:
    """Container for GCS file stat."""

    def __init__(
        self,
        filename: str,
        st_size: int,
        etag: str,
        st_ctime: float,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        is_dir: bool = False,
    ):
        """Initialize.

        Args:
            filename: A Google Cloud Storage filename of form '/bucket/filename'.
            st_size: File size in bytes.
            etag: Hex digest of the MD5 hash of the file's content.
            st_ctime: POSIX file creation time.
            content_type: Content type.
            metadata: A dict of user-specified options when creating the file.
            is_dir: True if this represents a directory.
        """
        self.filename = filename
        self.is_dir = is_dir
        self.st_size = None
        self.st_ctime = None
        self.etag = None
        self.content_type = content_type
        self.metadata = metadata

        if not is_dir:
            self.st_size = int(st_size)
            self.st_ctime = float(st_ctime)
            if etag[0] == '"' and etag[-1] == '"':
                etag = etag[1:-1]
            self.etag = etag

    def __repr__(self) -> str:
        if self.is_dir:
            return f'(directory: {self.filename})'

        return (
            f'(filename: {self.filename}, st_size: {self.st_size}, '
            f'st_ctime: {self.st_ctime}, etag: {self.etag}, '
            f'content_type: {self.content_type}, metadata: {self.metadata})'
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, GCSFileStat):
            return False
        return self.filename == other.filename

    def __hash__(self) -> int:
        if self.etag:
            return hash(self.etag)
        return hash(self.filename)


CSFileStat = GCSFileStat


from typing import Dict, Optional

def get_stored_content_length(headers: Dict[str, str]) -> int:
    return int(headers.get('x-goog-stored-content-length', headers.get('content-length', 0)))



from typing import Dict

def get_metadata(headers: Dict[str, str]) -> Dict[str, str]:
    """Extracts user-defined metadata from HTTP response headers.

    Args:
        headers: A dictionary of headers from the HTTP response.

    Returns:
        A dictionary containing metadata headers that match valid prefixes.
    """
    return {k: v for k, v in headers.items() if k.lower().startswith(tuple(_GCS_METADATA))}

def validate_bucket_name(name: str) -> None:
    """Validate a Google Storage bucket name.

    Args:
        name: A Google Storage bucket name with no prefix or suffix.

    Raises:
        ValueError: If the name is invalid.
    """
    _validate_path(name)
    if not _GCS_BUCKET_REGEX.match(name):
        raise ValueError(
            'Bucket should be 3-63 characters long using only a-z, 0-9, underscore, dash, or dot. Got: %s' % name
        )


def validate_bucket_path(path: str) -> None:
    """Validate a Google Cloud Storage bucket path.

    Args:
        path: A Google Storage bucket path. It should have the form '/bucket'.

    Raises:
        ValueError: If the path is invalid.
    """
    _validate_path(path)
    if not _GCS_BUCKET_PATH_REGEX.match(path):
        raise ValueError('Bucket should have format /bucket. Got: %s' % path)


def validate_file_path(path: str) -> None:
    """Validate a Google Cloud Storage file path.

    Args:
        path: A Google Storage file path. It should have the form '/bucket/filename'.

    Raises:
        ValueError: If the path is invalid.
    """
    _validate_path(path)
    if not _GCS_FULLPATH_REGEX.match(path):
        raise ValueError('Path should have format /bucket/filename. Got: %s' % path)


def _process_path_prefix(path_prefix: str) -> Tuple[str, Optional[str]]:
    """Validate and process a Google Cloud Storage path prefix.

    Args:
        path_prefix: A Google Cloud Storage path prefix of format '/bucket/prefix', '/bucket/', or '/bucket'.

    Raises:
        ValueError: If the path is invalid.

    Returns:
        A tuple of (/bucket, prefix). Prefix can be None.
    """
    _validate_path(path_prefix)
    if not _GCS_PATH_PREFIX_REGEX.match(path_prefix):
        raise ValueError('Path prefix should have format /bucket, /bucket/, or /bucket/prefix. Got: %s' % path_prefix)
    bucket_name_end = path_prefix.find('/', 1)
    bucket = path_prefix
    prefix = None
    if bucket_name_end != -1:
        bucket = path_prefix[:bucket_name_end]
        prefix = path_prefix[bucket_name_end + 1:] or None
    return bucket, prefix


def _validate_path(path: str) -> None:
    """Basic validation of Google Storage paths.

    Args:
        path: A Google Storage path. It should have the form '/bucket/filename' or '/bucket'.

    Raises:
        ValueError: If the path is invalid.
        TypeError: If the path is not of type str.
    """
    if not path:
        raise ValueError('Path is empty')
    if not isinstance(path, str):
        raise TypeError(f'Path should be a string. Got: {type(path)} ({path})')


from typing import Dict

def validate_options(options: Dict[str, str]) -> None:
    """Validates Google Cloud Storage options.

    Args:
        options: A dictionary of options to pass to Google Cloud Storage.

    Raises:
        ValueError: If an option is not supported.
        TypeError: If an option key or value is not of type str.
    """
    if not options:
        return

    valid_prefixes = tuple(_GCS_OPTIONS)  # Convert to tuple for efficient `startswith` checks

    for key, value in options.items():
        if not isinstance(key, str):
            raise TypeError(f"Option key '{key}' must be a string.")
        if not key.lower().startswith(valid_prefixes):
            raise ValueError(f"Option '{key}' is not supported.")
        if not isinstance(value, str):
            raise TypeError(f"Value '{value}' for option '{key}' must be a string.")



def http_time_to_posix(http_time: str) -> float:
    """Convert HTTP time format to POSIX time.

    Args:
        http_time: Time in RFC 2616 format (e.g., "Mon, 20 Nov 1995 19:12:08 GMT").

    Returns:
        A float of seconds from the Unix epoch.
    """
    if http_time:
        return email_utils.mktime_tz(email_utils.parsedate_tz(http_time))


def posix_time_to_http(posix_time: float) -> str:
    """Convert POSIX time to HTTP header time format.

    Args:
        posix_time: Unix time.

    Returns:
        A datetime string in RFC 2616 format.
    """
    if posix_time:
        return email_utils.formatdate(posix_time, usegmt=True)


_DT_FORMAT = '%Y-%m-%dT%H:%M:%S'


def dt_str_to_posix(dt_str: str) -> float:
    """Convert a datetime string to POSIX time.

    Args:
        dt_str: A datetime string in the format '%Y-%m-%dT%H:%M:%S.%fZ'.

    Returns:
        A float of seconds from the Unix epoch.
    """
    parsable, _ = dt_str.split('.')
    dt = datetime.datetime.strptime(parsable, _DT_FORMAT)
    return calendar.timegm(dt.utctimetuple())


def posix_to_dt_str(posix: float) -> str:
    """Convert POSIX time to a datetime string.

    Args:
        posix: A float of seconds from the Unix epoch.

    Returns:
        A datetime string.
    """
    dt = datetime.datetime.utcfromtimestamp(posix)
    dt_str = dt.strftime(_DT_FORMAT)
    return dt_str + '.000Z'


def local_run() -> bool:
    """Determine whether to use the GCS dev appserver stub.

    Returns:
        True if running locally, False otherwise.
    """
    server_software = os.environ.get('SERVER_SOFTWARE', '')
    if not server_software:
        return True
    if 'remote_api' in server_software:
        return False
    if server_software.startswith(('Development', 'testutil')):
        return True
    return False


def local_api_url() -> str:
    """Return the URL for GCS emulation on the dev appserver.

    Returns:
        The URL for the local GCS endpoint.
    """
    return f'http://{os.environ.get("HTTP_HOST")}{LOCAL_GCS_ENDPOINT}'


def memory_usage(method):
    """Log memory usage before and after a method."""
    def wrapper(*args, **kwargs):
        logging.info('Memory before method %s is %s.', method.__name__, sys.getsizeof(method))
        result = method(*args, **kwargs)
        logging.info('Memory after method %s is %s.', method.__name__, sys.getsizeof(method))
        return result
    return wrapper


def _add_ns(tagname: str) -> str:
    """Add XML namespace to a tag name.

    Args:
        tagname: The tag name.

    Returns:
        The tag name with the namespace.
    """
    return f'{{{CS_XML_NS}}}{tagname}'


_T_CONTENTS = _add_ns('Contents')
_T_LAST_MODIFIED = _add_ns('LastModified')
_T_ETAG = _add_ns('ETag')
_T_KEY = _add_ns('Key')
_T_SIZE = _add_ns('Size')
_T_PREFIX = _add_ns('Prefix')
_T_COMMON_PREFIXES = _add_ns('CommonPrefixes')
_T_NEXT_MARKER = _add_ns('NextMarker')
_T_IS_TRUNCATED = _add_ns('IsTruncated')