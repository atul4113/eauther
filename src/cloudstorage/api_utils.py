# Copyright 2013 Google Inc. All Rights Reserved.
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

"""Util functions and classes for cloudstorage_api."""

__all__ = [
    'set_default_retry_params',
    'RetryParams',
]

import copy
import http.client
import logging
import math
import os
import threading
import time
import urllib.parse

from google.cloud import storage  # Replace App Engine storage with Google Cloud Storage
from google.cloud.exceptions import GoogleCloudError  # For retriable exceptions
from google.cloud.ndb import tasklets, utils  # Replace App Engine NDB with Cloud NDB

# Define retriable exceptions for Google Cloud Storage
_RETRIABLE_EXCEPTIONS = (
    GoogleCloudError,
    http.client.HTTPException,
    ConnectionError,
    TimeoutError,
)

_thread_local_settings = threading.local()
_thread_local_settings.default_retry_params = None


def set_default_retry_params(retry_params):
    """Set a default RetryParams for the current thread and request."""
    _thread_local_settings.default_retry_params = copy.copy(retry_params)


def _get_default_retry_params():
    """Get default RetryParams for the current request and thread.

    Returns:
        A new instance of the default RetryParams.
    """
    default = getattr(_thread_local_settings, 'default_retry_params', None)
    if default is None or not default.belong_to_current_request():
        return RetryParams()
    else:
        return copy.copy(default)


def _quote_filename(filename):
    """Quote filename to use as a valid URI path.

    Args:
        filename: User-provided filename. /bucket/filename.

    Returns:
        The filename properly quoted to use as a URI path component.
    """
    return urllib.parse.quote(filename)


def _unquote_filename(filename):
    """Unquote a valid URI path back to its filename.

    This is the opposite of _quote_filename.

    Args:
        filename: A quoted filename. /bucket/some%20filename.

    Returns:
        The filename unquoted.
    """
    return urllib.parse.unquote(filename)


def _should_retry(response):
    """Given a response, decide whether to retry the request.

    Args:
        response: A response object from Google Cloud Storage.

    Returns:
        bool: True if the request should be retried, False otherwise.
    """
    if response.status_code == http.client.REQUEST_TIMEOUT:
        return True
    return 500 <= response.status_code < 600


class _RetryWrapper:
    """A wrapper that adds retry logic around any tasklet."""

    def __init__(self, retry_params, retriable_exceptions=_RETRIABLE_EXCEPTIONS, should_retry=lambda r: False):
        """Initialize the retry wrapper.

        Args:
            retry_params: A RetryParams instance.
            retriable_exceptions: A tuple of exception classes that are retriable.
            should_retry: A function that takes a result and returns True if the result should be retried.
        """
        self.retry_params = retry_params
        self.retriable_exceptions = retriable_exceptions
        self.should_retry = should_retry

    @tasklets.tasklet
    def run(self, tasklet, **kwargs):
        """Run a tasklet with retry logic.

        Args:
            tasklet: The tasklet to run.
            **kwargs: Keyword arguments to pass to the tasklet.

        Raises:
            Exception: The exception from the last retry if all retries fail.

        Returns:
            The result from the tasklet.
        """
        start_time = time.time()
        n = 1

        while True:
            exception = None
            result = None
            got_result = False

            try:
                result = yield tasklet(**kwargs)
                got_result = True
                if not self.should_retry(result):
                    raise tasklets.Return(result)
            except self.retriable_exceptions as e:
                exception = e

            if n == 1:
                logging.debug('Tasklet is %r', tasklet)

            delay = self.retry_params.delay(n, start_time)

            if delay <= 0:
                logging.debug(
                    'Tasklet failed after %s attempts and %s seconds in total',
                    n, time.time() - start_time
                )
                if got_result:
                    raise tasklets.Return(result)
                elif exception is not None:
                    raise exception
                else:
                    assert False, 'Should never reach here.'

            if got_result:
                logging.debug('Got result %r from tasklet.', result)
            else:
                logging.debug('Got exception "%r" from tasklet.', exception)
            logging.debug('Retry in %s seconds.', delay)
            n += 1
            yield tasklets.sleep(delay)


class RetryParams:
    """Retry configuration parameters."""

    _DEFAULT_USER_AGENT = 'Google Cloud Python GCS Client'

    def __init__(self, backoff_factor=2.0, initial_delay=0.1, max_delay=10.0, min_retries=3, max_retries=6,
                 max_retry_period=30.0, urlfetch_timeout=None, save_access_token=False, _user_agent=None):
        """Initialize RetryParams.

        Args:
            backoff_factor: Exponential backoff multiplier.
            initial_delay: Seconds to delay for the first retry.
            max_delay: Max seconds to delay for every retry.
            min_retries: Min number of times to retry. Capped by max_retries.
            max_retries: Max number of times to retry. Set to 0 for no retry.
            max_retry_period: Max total seconds spent on retry.
            urlfetch_timeout: Timeout for urlfetch in seconds.
            save_access_token: Persist access token to avoid excessive API usage.
            _user_agent: User agent string for requests.
        """
        self.backoff_factor = self._check('backoff_factor', backoff_factor)
        self.initial_delay = self._check('initial_delay', initial_delay)
        self.max_delay = self._check('max_delay', max_delay)
        self.max_retry_period = self._check('max_retry_period', max_retry_period)
        self.max_retries = self._check('max_retries', max_retries, True, int)
        self.min_retries = self._check('min_retries', min_retries, True, int)
        if self.min_retries > self.max_retries:
            self.min_retries = self.max_retries

        self.urlfetch_timeout = None
        if urlfetch_timeout is not None:
            self.urlfetch_timeout = self._check('urlfetch_timeout', urlfetch_timeout)
        self.save_access_token = self._check('save_access_token', save_access_token, True, bool)
        self._user_agent = _user_agent or self._DEFAULT_USER_AGENT

        self._request_id = os.getenv('REQUEST_LOG_ID')

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def _check(cls, name, val, can_be_zero=False, val_type=float):
        """Check init arguments.

        Args:
            name: Name of the argument.
            val: Value to check.
            can_be_zero: Whether the value can be zero.
            val_type: Expected type of the value.

        Returns:
            The value.

        Raises:
            ValueError: If the value is invalid.
            TypeError: If the value type is invalid.
        """
        valid_types = [val_type]
        if val_type is float:
            valid_types.append(int)

        if not isinstance(val, tuple(valid_types)):
            raise TypeError(f'Expect type {val_type.__name__} for parameter {name}')
        if val < 0:
            raise ValueError(f'Value for parameter {name} has to be greater than 0')
        if not can_be_zero and val == 0:
            raise ValueError(f'Value for parameter {name} cannot be 0')
        return val

    def belong_to_current_request(self):
        """Check if the retry params belong to the current request."""
        return os.getenv('REQUEST_LOG_ID') == self._request_id

    def delay(self, n, start_time):
        """Calculate delay before the next retry.

        Args:
            n: The number of the current attempt.
            start_time: The time when retry started in Unix time.

        Returns:
            Number of seconds to wait before the next retry. -1 if retry should give up.
        """
        if (n > self.max_retries or
                (n > self.min_retries and time.time() - start_time > self.max_retry_period)):
            return -1
        return min(math.pow(self.backoff_factor, n - 1) * self.initial_delay, self.max_delay)


# def _run_until_rpc():
#   """Eagerly evaluate tasklets until it is blocking on some RPC.
#
#   Usually ndb eventloop el isn't run until some code calls future.get_result().
#
#   When an async tasklet is called, the tasklet wrapper evaluates the tasklet
#   code into a generator, enqueues a callback _help_tasklet_along onto
#   the el.current queue, and returns a future.
#
#   _help_tasklet_along, when called by the el, will
#   get one yielded value from the generator. If the value if another future,
#   set up a callback _on_future_complete to invoke _help_tasklet_along
#   when the dependent future fulfills. If the value if a RPC, set up a
#   callback _on_rpc_complete to invoke _help_tasklet_along when the RPC fulfills.
#   Thus _help_tasklet_along drills down
#   the chain of futures until some future is blocked by RPC. El runs
#   all callbacks and constantly check pending RPC status.
#   """
#   el = eventloop.get_event_loop()
#   while el.current:
#     el.run0()


def _eager_tasklet(tasklet):
    """Decorator to make a tasklet run eagerly."""

    @utils.wrapping(tasklet)
    def eager_wrapper(*args, **kwargs):
        fut = tasklet(*args, **kwargs)
        _run_until_rpc()
        return fut

    return eager_wrapper