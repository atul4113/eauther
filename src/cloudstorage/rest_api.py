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

"""Base and helper classes for Google RESTful APIs."""

import random
import time
from typing import List, Optional, Dict, Any, Tuple

from google.cloud import ndb
from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account

__all__ = ['add_sync_methods']


def _make_sync_method(name):
    """Helper to synthesize a synchronous method from an async method name.

    Used by the @add_sync_methods class decorator below.

    Args:
        name: The name of the synchronous method.

    Returns:
        A method (with first argument 'self') that retrieves and calls
        self.<name>, passing its own arguments, expects it to return a
        Future, and then waits for and returns that Future's result.
    """

    def sync_wrapper(self, *args, **kwds):
        method = getattr(self, name)
        future = method(*args, **kwds)
        return future.result()

    return sync_wrapper


def add_sync_methods(cls):
    """Class decorator to add synchronous methods corresponding to async methods.

    This modifies the class in place, adding additional methods to it.
    If a synchronous method of a given name already exists it is not
    replaced.

    Args:
        cls: A class.

    Returns:
        The same class, modified in place.
    """
    for name in list(cls.__dict__.keys()):
        if name.endswith('_async'):
            sync_name = name[:-6]
            if not hasattr(cls, sync_name):
                setattr(cls, sync_name, _make_sync_method(name))
    return cls


class _TokenStorage(ndb.Model):
    """Entity to store authentication tokens in Datastore."""

    token = ndb.StringProperty()
    expires = ndb.FloatProperty()


@ndb.tasklet
def _make_token_async(scopes: List[str], service_account_id: Optional[str] = None) -> Tuple[str, float]:
    """Get a fresh authentication token.

    Args:
        scopes: A list of scopes.
        service_account_id: Internal-use only.

    Returns:
        A tuple (token, expiration_time) where expiration_time is
        seconds since the epoch.
    """
    credentials = service_account.Credentials.from_service_account_file(
        'path/to/service-account.json', scopes=scopes
    )
    auth_session = AuthorizedSession(credentials)
    token = credentials.token
    expires_at = credentials.expiry.timestamp() if credentials.expiry else time.time() + 3600
    raise ndb.Return((token, expires_at))


class _RestApi:
    """Base class for REST-based API wrapper classes.

    This class manages authentication tokens and request retries. All
    APIs are available as synchronous and async methods; synchronous
    methods are synthesized from async ones by the add_sync_methods()
    function in this module.

    WARNING: Do NOT directly use this api. It's an implementation detail
    and is subject to change at any release.
    """

    def __init__(
        self,
        scopes: List[str],
        service_account_id: Optional[str] = None,
        token_maker=None,
        retry_params=None,
    ):
        """Constructor.

        Args:
            scopes: A scope or a list of scopes.
            service_account_id: Internal use only.
            token_maker: An asynchronous function of the form
              (scopes, service_account_id) -> (token, expires).
            retry_params: An instance of api_utils.RetryParams. If None, the
              default for current thread will be used.
        """
        if isinstance(scopes, str):
            scopes = [scopes]
        self.scopes = scopes
        self.service_account_id = service_account_id
        self.make_token_async = token_maker or _make_token_async
        self.retry_params = retry_params or api_utils._get_default_retry_params()
        self.user_agent = {'User-Agent': self.retry_params._user_agent}
        self.expiration_headroom = random.randint(60, 240)

    @ndb.tasklet
    def get_token_async(self, refresh: bool = False) -> str:
        """Get an authentication token.

        The token is cached in Datastore, keyed by the scopes argument.
        Uses a random token expiration headroom value generated in the constructor
        to eliminate a burst of token refresh requests.

        Args:
            refresh: If True, ignore a cached token; default False.

        Returns:
            An authentication token. This token is guaranteed to be non-expired.
        """
        key = f"{self.service_account_id},{','.join(self.scopes)}"
        ts = yield _TokenStorage.get_by_id_async(key)
        if refresh or ts is None or ts.expires < (time.time() + self.expiration_headroom):
            token, expires_at = yield self.make_token_async(self.scopes, self.service_account_id)
            ts = _TokenStorage(id=key, token=token, expires=expires_at)
            yield ts.put_async()
        raise ndb.Return(ts.token)

    @ndb.tasklet
    def do_request_async(
        self,
        url: str,
        method: str = 'GET',
        headers: Optional[Dict[str, str]] = None,
        payload: Optional[Any] = None,
        deadline: Optional[float] = None,
    ):
        """Issue one HTTP request.

        It performs async retries using tasklets.

        Args:
            url: The URL to fetch.
            method: The HTTP method to use.
            headers: The HTTP headers.
            payload: The data to submit in the request.
            deadline: The deadline in which to make the call.

        Returns:
            A tuple (status_code, headers, content).
        """
        headers = headers or {}
        headers.update(self.user_agent)
        token = yield self.get_token_async()
        if token:
            headers['Authorization'] = f'Bearer {token}'

        session = AuthorizedSession(service_account.Credentials.from_service_account_file(
            'path/to/service-account.json', scopes=self.scopes
        ))
        response = yield session.request(
            method, url, headers=headers, data=payload, timeout=deadline
        )
        raise ndb.Return((response.status_code, response.headers, response.content))


_RestApi = add_sync_methods(_RestApi)