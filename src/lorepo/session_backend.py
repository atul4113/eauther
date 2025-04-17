from django.contrib.sessions.backends.db import SessionStore as DBStore
from django.core.exceptions import SuspiciousOperation
from django.db import IntegrityError, transaction
from gcloudc.db.backends.datastore.transaction import TransactionFailedError
from google.api_core.exceptions import Aborted
import time
import random
import logging

logger = logging.getLogger(__name__)

class SessionStore(DBStore):
    def save(self, must_create=False):
        """
        Saves the current session data to the database. If 'must_create' is True,
        a database error will be raised if the saving operation doesn't create a
        new entry (as opposed to possibly updating an existing entry).
        """
        if self.session_key is None:
            return self.create()
        
        data = self._get_session(no_load=must_create)
        obj = self.create_model_instance(data)
        max_retries = 5  # Increased retries
        retry_count = 0
        base_delay = 0.1  # 100ms

        while retry_count < max_retries:
            try:
                with transaction.atomic():
                    obj.save(force_insert=must_create, force_update=not must_create)
                return
            except (TransactionFailedError, Aborted, IntegrityError) as e:
                retry_count += 1
                if retry_count == max_retries:
                    logger.warning(f"Failed to save session after {max_retries} retries: {str(e)}")
                    # Don't raise the error, just log it and continue
                    return
                # Exponential backoff with jitter
                delay = base_delay * (2 ** retry_count) + random.uniform(0, 0.1)
                time.sleep(delay)

    def create(self):
        """
        Creates a new session instance in the database.
        """
        max_retries = 5
        retry_count = 0
        
        while retry_count < max_retries:
            self._session_key = self._get_new_session_key()
            try:
                self.save(must_create=True)
                self.modified = True
                return
            except (TransactionFailedError, Aborted, IntegrityError) as e:
                retry_count += 1
                if retry_count == max_retries:
                    logger.warning(f"Failed to create session after {max_retries} retries: {str(e)}")
                    # Generate a new session key and try one last time
                    self._session_key = self._get_new_session_key()
                    try:
                        self.save(must_create=True)
                        self.modified = True
                        return
                    except Exception:
                        # If we still fail, let the exception propagate
                        raise
                # Exponential backoff with jitter
                delay = 0.1 * (2 ** retry_count) + random.uniform(0, 0.1)
                time.sleep(delay) 