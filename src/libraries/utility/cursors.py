from google.appengine.datastore.datastore_query import Cursor


class CursorQueryMixin(object):
    def clone(self, *args, **kwargs):
        kwargs['_gae_cursor'] = getattr(self, '_gae_cursor', None)
        kwargs['_gae_start_cursor'] = getattr(self, '_gae_start_cursor', None)
        kwargs['_gae_end_cursor'] = getattr(self, '_gae_end_cursor', None)
        return super(CursorQueryMixin, self).clone(*args, **kwargs)


def get_cursor(queryset):
    list(queryset)  #make sure the results have been fetched
    try:
        cursor = queryset.query._gae_query_cursor
        return Cursor.to_websafe_string(cursor)
    except:
        import traceback
        import logging
        logging.error(traceback.format_exc())
        raise AssertionError('No cursor available for this query')


def set_cursor(queryset, start_cursor):
    queryset = queryset.all() #creates a queryset copy, so we don't modify the argument

    class CursorQuery(CursorQueryMixin, queryset.query.__class__):
        pass

    queryset.query = queryset.query.clone(klass=CursorQuery)
    cursor = Cursor.from_websafe_string(start_cursor)
    queryset.query._gae_start_cursor = cursor
    return queryset


class CursorPaginator(object):
    def __init__(self, queryset, batchsize=100, cursor=None):
        self._queryset = queryset
        self._batchsize = batchsize
        self._cursor = cursor


    def get_batch(self):
        if self._cursor is None:
            results = self._queryset[0:self._batchsize]
            self._cursor = get_cursor(results)
            return results
        else:
            results = set_cursor(self._queryset, self._cursor)
            results = results[0:self._batchsize]
            self._cursor = get_cursor(results)
            return results

    def get_cursor(self):
        return self._cursor

    def set_cursor(self, cursor):
        self._cursor = cursor

    def has_next(self, cursor):
        self.get_batch()
        next_cursor = self.get_cursor()
        # self.set_cursor(cursor)

        return next_cursor != cursor