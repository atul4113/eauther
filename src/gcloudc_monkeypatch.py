from django.db.models.sql.compiler import SQLCompiler


def patched_setup_query(self, with_col_aliases=False):
    """
    Monkey-patch to remove `with_col_aliases` from `get_select()` call.
    """
    self.select, self.klass_info, self.annotation_col_map = self.get_select()
    self.col_count = len(self.select)
    self.extra_order_by = ()
    self.group_by = None


# Apply the patch
SQLCompiler.setup_query = patched_setup_query

from django.db.models.sql.query import Query

from django.db.models.sql.query import Query


def patched_deferred_to_columns(self, columns=None):
    """
    Fully robust replacement for `deferred_to_data()` in Django 4.2.
    Handles all possible formats of deferred_loading.
    """
    if columns is None:
        columns = {}

    deferred_loading = getattr(self, "deferred_loading", None)

    # Case 1: deferred_loading is None or True (load all fields)
    if deferred_loading is None or deferred_loading is True:
        return columns

    # Case 2: deferred_loading is False (means load all fields)
    if deferred_loading is False:
        return columns

    # Case 3: deferred_loading is a tuple (standard case)
    try:
        if isinstance(deferred_loading, (tuple, list)) and len(deferred_loading) == 2:
            load_all, field_list = deferred_loading
            if not load_all and isinstance(field_list, (list, tuple)):
                for field in field_list:
                    try:
                        model = field.model._meta.concrete_model
                        if model not in columns:
                            columns[model] = set()
                        columns[model].add(field.column)
                    except AttributeError:
                        continue
    except (TypeError, IndexError):
        pass

    return columns


# Apply the patch globally
Query.deferred_to_data = patched_deferred_to_columns
