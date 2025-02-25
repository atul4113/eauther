from rest_framework.generics import GenericAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin


def get_cursor(self):
    """Returns the current cursor (page number)."""
    return self._cursor


def set_cursor(self, cursor):
    """Sets the cursor (page number)."""
    self._cursor = int(cursor)


class PageDataWithCursor:
    data = []
    more_count = 0
    cursor = None

    def __init__(self, data, more_count, cursor):
        self.data = data
        self.more_count = more_count if more_count > 0 else 0
        self.cursor = cursor


def get_data_with_cursor(query_set, cursor=None, serializer=None, context=None, batch_size=50):
    context = context if context else {}

    if cursor:
        query_set = set_cursor(query_set, cursor)

    count = query_set.count()
    query_set = query_set[0:batch_size]

    serialized_data = serializer(query_set, many=True, context=context).data if serializer else query_set

    more_count = count - batch_size
    new_cursor = get_cursor(query_set) if more_count > 0 else None

    return PageDataWithCursor(
        data=serialized_data,
        more_count=more_count,
        cursor=new_cursor
    )


class RetrieveOrListAPIView(ListModelMixin, RetrieveModelMixin, GenericAPIView):
    lookup_field = 'pk'
    lookup_url_kwarg = None

    def get(self, request, *args, **kwargs):
        lookup_name = self.lookup_url_kwarg if self.lookup_url_kwarg else self.lookup_field
        if kwargs.get(lookup_name):
            return self.retrieve(request, args, kwargs)
        else:
            return self.list(request, args, kwargs)


class CreateUpdateDestroyAPIView(CreateAPIView, UpdateAPIView, DestroyAPIView, GenericAPIView):

    def put(self, request, *args, **kwargs):
        kwargs.update({'partial': True})
        return self.update(request, *args, **kwargs)
