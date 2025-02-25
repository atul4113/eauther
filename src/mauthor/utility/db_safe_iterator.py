import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))


def get_cursor(self):
    """Returns the current cursor (page number)."""
    return self._cursor


def set_cursor(self, cursor):
    """Sets the cursor (page number)."""
    self._cursor = int(cursor)


def safe_iterate(queryset, batch_size=200):
    '''
    Generator to iterate through a query set in batches implemented using coursors instead of offsets.
    !!! Do not use with queries containg __in filters - will loop forever.
    !!! Do not use with queries containg parameter=None - an exception will occur in second execution.
    !!! When using queries containing inequality filter (__lte __gte) duplicated results might be returned.
    "Because the != and IN operators are implemented with multiple queries, queries that use them do not support cursors."
    Also:
    https://cloud.google.com/appengine/docs/python/datastore/queries?hl=en#Python_Limitations_of_cursors
    '''
    results = queryset[0:batch_size]
    while len(results):
        cursor = get_cursor(results)
        yield results
        results = set_cursor(queryset, cursor)
        results = results[0:batch_size]
