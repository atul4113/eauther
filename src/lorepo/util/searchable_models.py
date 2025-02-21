import logging
import re
import traceback

from django.db import models

from libraries.utility.environment import get_versioned_module
from libraries.utility.queues import trigger_backend_task, TaskQueue
from google.appengine.api.search import search


class EnableBackendObjectMethod(models.Model):
    retry_exceptions = None
    backend_module = 'download'
    queue_name = TaskQueue.DEFAULT

    class Meta:
        abstract = True

    def object_method_in_backend(self, method):
        url = '/util/object_method/%s/%s/%s/%s' % (self.__module__, self.__class__.__name__, method, self.id)
        trigger_backend_task(url, target=get_versioned_module(self.backend_module), queue_name=self.queue_name)

    def try_or_run_backend(self, method, exeptions=None):
        if (exeptions is None) and (self.retry_exceptions is not None):
            exeptions = self.retry_exceptions

        if exeptions is None:
            getattr(self, method)()
            return

        try:
            getattr(self, method)()
        except exeptions as e:
            self.object_method_in_backend(method)
            logging.error('Retry exception:')
            logging.error(e)


class SearchableModel(EnableBackendObjectMethod):
    """
    Abstract model that supports Database entities automatically save to GAE Full Text Search
    Fields that have to been saved in Search should be included in "_search_indexed_fields" property
    """

    class Meta:
        abstract = True

    backend_module = 'translations'
    queue_name = TaskQueue.SEARCH

    search_index = None
    doc_id = None
    entity_id = None

    def get_index(self):
        if self.search_index is None:
            index_name = self._meta.db_table
            self.search_index = search.Index(name=index_name)
        return self.search_index

    def get_doc_id(self):
        if self.doc_id is None:
            self.doc_id = str(self.pk)
        return self.doc_id

    def save(self, *args, **kwargs):
        super(SearchableModel, self).save(*args, **kwargs)
        if hasattr(self, '_search_indexed_fields'):
            self.add_to_search_index()

    def get_document_instance(self):
        doc_id = self.get_doc_id()
        fields = []
        for field in self._search_indexed_fields:
            fields.append(search.TextField(name=field, value=str(getattr(self, field, ""))))
            if hasattr(self, "tokenize") and self.tokenize:
                if '_id' == field[-3:]:
                    continue
                fields.append(search.TextField(name="tokenized_values", value=self.tokenized_value(field)))
        document = search.Document(doc_id=doc_id, fields=fields)
        return document

    def add_to_search_index(self):
        document = self.get_document_instance()
        try:
            self.get_index().put(document)
        except search.Error:
            logging.exception('Put failed')
            logging.error(traceback.format_exc())
            self.save_search_index_in_backend()

    def save_search_index_in_backend(self):
        self.object_method_in_backend('add_to_search_index')

    def delete(self, *args, **kwargs):
        if hasattr(self, '_search_indexed_fields'):
            self.remove_from_search_index()
        super(SearchableModel, self).delete(*args, **kwargs)

    def remove_from_search_index(self):
        self.get_index().delete(self.get_doc_id())

    @classmethod
    def search(cls, term, cursor_string=None, limit=20, **kwargs):
        if not cursor_string:
            cursor = search.Cursor()
        else:
            cursor = search.Cursor(web_safe_string=cursor_string)
        term = re.sub(r'([\s"\']+)', ' ', term)
        term = list(filter(bool, term.split(" ")))
        query = '"' + '" AND "'.join(term) + '"'

        if kwargs:
            kwargs_query = []
            for k, v in list(kwargs.items()):
                kwargs_query.append("%s=%s" % (k, v))
            kwargs_query = ' AND '.join(kwargs_query)
            query = '%s AND (%s)' % (kwargs_query, query)

        sort_options = None
        if 'priority' in cls._search_indexed_fields:
            sort_options = search.SortOptions(expressions=[
                search.SortExpression(expression='priority', direction=search.SortExpression.DESCENDING, default_value='')
            ])

        index_search = cls().get_index().search(
            search.Query(
                query_string=query,
                options=search.QueryOptions(limit=limit, cursor=cursor, number_found_accuracy=100, sort_options=sort_options)
            )
        )
        result = {
            'number_found': index_search.number_found,
            'results': cls.get_results(index_search),
            'cursor': index_search.cursor.web_safe_string if index_search.cursor else None
        }
        return result

    @classmethod
    def get_results(cls, search_results):
        return cls.objects.filter(pk__in=[doc.doc_id for doc in search_results])

    def tokenize_phrase(self, phrase, start_word = 2):
        a = set()
        for word in phrase.split():
            for i in range(1,len(word)+1):
                if i > start_word:
                    a.add(word[0:i])
        return ' '.join(a)

    def tokenized_value(self, field):
        text = str(getattr(self, field, ""))
        text = re.sub(r"[\,;\/\-\(\)\!#$%\^\&\*=\|]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return self.tokenize_phrase(text)


class MultiKindSearchableModel(SearchableModel):
    """
    Abstract model that supports Database entities automatically save to GAE Full Text Search
    Fields that have to been saved in Search should be included in "_search_indexed_fields" property
    This model supports search in different kinds which share common fields.
    Classes' names should be included in _multi_kind_search and classmethod get_model(kind)
    should be implemented and have to return proper model for each kind.
    """

    class Meta:
        abstract = True

    def get_index(self):
        if self.search_index is None:
            index_name = "_multi_%s" % '_'.join(self._multi_kind_search)
            self.search_index = search.Index(name=index_name)
        return self.search_index

    def get_doc_id(self):
        if self.doc_id is None:
            self.doc_id = str("%s__%s" % (self.__class__.__name__, self.pk))
        return self.doc_id

    @classmethod
    def get_model(cls, kind):
        raise NotImplementedError('get_model() is not implemeted in class %s' % cls.__name__)

    @classmethod
    def get_results(cls, search_results):
        results = []
        for doc in search_results:
            doc_id = doc.doc_id.split('__')
            kind = doc_id[0]
            key = doc_id[1]
            model = cls.get_model(kind)
            results.append(model.objects.get(pk=key))
        return results


class Indexable(SearchableModel):

    def save(self, *args, **kwargs):
        # save data only in full text search engine
        if hasattr(self, '_search_indexed_fields'):
            self.add_to_search_index()

    def delete(self, *args, **kwargs):
        if hasattr(self, '_search_indexed_fields'):
            self.remove_from_search_index()

    def get_document_instance(self):
        doc_id = self.get_doc_id()
        fields = []
        for field in self._search_indexed_fields:  # create normal fields
            fields.append(search.TextField(name=field, value=str(getattr(self, field, ""))))

        for field in self._search_indexed_tokenized_fields:  # create tokenized fields
            fields.append(search.TextField(name="%s_tokenized_values" % field, value=self.tokenized_value(field)))
        document = search.Document(doc_id=doc_id, fields=fields)
        return document

    def add_to_search_index(self):
        document = self.get_document_instance()

        try:
            self.get_index().put(document)
        except search.Error:
            logging.exception('Put failed')
            logging.error(traceback.format_exc())
            self.save_search_index_in_backend()

    @classmethod
    def search(cls, query, page=1, limit=10, sort_by_field=None, direction=None, **kwargs):
        if kwargs:
            kwargs_query = []
            for k, v in list(kwargs.items()):
                kwargs_query.append("%s=%s" % (k, v))
            kwargs_query = ' AND '.join(kwargs_query)
            query = '%s AND (%s)' % (kwargs_query, query)

        sort_options = None

        if len(cls._sorted_fields) > 0:
            sort_by_field = cls._sorted_fields[0]

        if sort_by_field is not None:
            sort_options = search.SortOptions(expressions=[
                search.SortExpression(expression=sort_by_field, direction=search.SortExpression.ASCENDING, default_value='')
            ])

        index_search = cls().get_index().search(
            search.Query(
                query_string=query,
                options=search.QueryOptions(limit=limit, offset=(page-1)*limit, number_found_accuracy=100,
                                            sort_options=sort_options)
            )
        )

        return {
            'number_found': index_search.number_found,
            'results': index_search,
            'cursor': index_search.cursor.web_safe_string if index_search.cursor else None
        }
