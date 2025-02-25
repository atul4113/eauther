from django.core.paginator import Paginator, EmptyPage
import logging


class CursorPaginator:
    def __init__(self, queryset, batchsize=100, cursor=None):
        self._queryset = queryset
        self._batchsize = batchsize
        self._cursor = int(cursor) if cursor else 1  # Default to page 1
        self._paginator = Paginator(queryset, batchsize)

    def get_batch(self):
        try:
            results = self._paginator.page(self._cursor)
            self._cursor += 1  # Move to the next page
            return results.object_list
        except EmptyPage:
            return []

    def get_cursor(self):
        """Returns the current cursor (page number)."""
        return self._cursor

    def set_cursor(self, cursor):
        """Sets the cursor (page number)."""
        self._cursor = int(cursor)

    def has_next(self):
        """Checks if there's another batch after the current one."""
        return self._cursor <= self._paginator.num_pages
