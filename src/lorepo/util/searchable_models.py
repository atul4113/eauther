import logging
import re
import traceback
from django.db import models
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models import Q
from libraries.utility.environment import get_versioned_module
from libraries.utility.queues import trigger_backend_task, TaskQueue


class EnableBackendObjectMethod(models.Model):
    retry_exceptions = None
    backend_module = 'download'
    queue_name = TaskQueue.DEFAULT

    class Meta:
        abstract = True

    def object_method_in_backend(self, method):
        url = '/util/object_method/%s/%s/%s/%s' % (self.__module__, self.__class__.__name__, method, self.id)
        trigger_backend_task(url, target=get_versioned_module(self.backend_module), queue_name=self.queue_name)

    def try_or_run_backend(self, method, exceptions=None):
        if (exceptions is None) and (self.retry_exceptions is not None):
            exceptions = self.retry_exceptions

        if exceptions is None:
            getattr(self, method)()
            return

        try:
            getattr(self, method)()
        except exceptions as e:
            self.object_method_in_backend(method)
            logging.error('Retry exception:')
            logging.error(e)


class SearchableModel(EnableBackendObjectMethod):
    """
    Abstract model that supports Database entities automatically saved to a search index.
    Fields that need to be indexed should be included in "_search_indexed_fields" property.
    """

    class Meta:
        abstract = True

    backend_module = 'translations'
    queue_name = TaskQueue.SEARCH

    def save(self, *args, **kwargs):
        super(SearchableModel, self).save(*args, **kwargs)
        if hasattr(self, '_search_indexed_fields'):
            self.add_to_search_index()

    def add_to_search_index(self):
        """
        Adds the object to the search index.
        """
        try:
            # Update the search index for the object
            self.update_search_index()
        except Exception as e:
            logging.error(f"Failed to add to search index: {e}")
            logging.error(traceback.format_exc())
            self.save_search_index_in_backend()

    def save_search_index_in_backend(self):
        """
        Schedules the object to be added to the search index in the background.
        """
        self.object_method_in_backend('add_to_search_index')

    def delete(self, *args, **kwargs):
        if hasattr(self, '_search_indexed_fields'):
            self.remove_from_search_index()
        super(SearchableModel, self).delete(*args, **kwargs)

    def remove_from_search_index(self):
        """
        Removes the object from the search index.
        """
        # Implement search index removal logic here
        pass

    @classmethod
    def search(cls, term, cursor_string=None, limit=20, **kwargs):
        """
        Searches for objects matching the given term.
        """
        if not term:
            return {'number_found': 0, 'results': [], 'cursor': None}

        # Use Django's built-in search functionality
        search_vector = SearchVector(*cls._search_indexed_fields)
        search_query = SearchQuery(term)
        search_rank = SearchRank(search_vector, search_query)

        queryset = cls.objects.annotate(
            rank=search_rank
        ).filter(rank__gte=0.1).order_by('-rank')[:limit]

        return {
            'number_found': queryset.count(),
            'results': queryset,
            'cursor': None  # Cursor functionality is not supported in Django's built-in search
        }

    def tokenize_phrase(self, phrase, start_word=2):
        """
        Tokenizes a phrase for search indexing.
        """
        tokens = set()
        for word in phrase.split():
            for i in range(1, len(word) + 1):
                if i > start_word:
                    tokens.add(word[0:i])
        return ' '.join(tokens)

    def tokenized_value(self, field):
        """
        Returns a tokenized value for a given field.
        """
        text = str(getattr(self, field, ""))
        text = re.sub(r"[\,;\/\-\(\)\!#$%\^\&\*=\|]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return self.tokenize_phrase(text)


class MultiKindSearchableModel(SearchableModel):
    """
    Abstract model that supports searching across multiple kinds (models).
    """

    class Meta:
        abstract = True

    @classmethod
    def get_model(cls, kind):
        """
        Returns the model class for the given kind.
        """
        raise NotImplementedError('get_model() is not implemented in class %s' % cls.__name__)

    @classmethod
    def get_results(cls, search_results):
        """
        Returns the results of a search query.
        """
        results = []
        for doc in search_results:
            doc_id = doc.doc_id.split('__')
            kind = doc_id[0]
            key = doc_id[1]
            model = cls.get_model(kind)
            results.append(model.objects.get(pk=key))
        return results


class Indexable(SearchableModel):
    """
    Abstract model that supports indexing in a search engine.
    """

    def save(self, *args, **kwargs):
        # Save data only in the full-text search engine
        if hasattr(self, '_search_indexed_fields'):
            self.add_to_search_index()

    def delete(self, *args, **kwargs):
        if hasattr(self, '_search_indexed_fields'):
            self.remove_from_search_index()

    @classmethod
    def search(cls, query, page=1, limit=10, sort_by_field=None, direction=None, **kwargs):
        """
        Searches for objects matching the given query.
        """
        if not query:
            return {'number_found': 0, 'results': [], 'cursor': None}

        # Use Django's built-in search functionality
        search_vector = SearchVector(*cls._search_indexed_fields)
        search_query = SearchQuery(query)
        search_rank = SearchRank(search_vector, search_query)

        queryset = cls.objects.annotate(
            rank=search_rank
        ).filter(rank__gte=0.1).order_by('-rank')[(page - 1) * limit:page * limit]

        return {
            'number_found': queryset.count(),
            'results': queryset,
            'cursor': None  # Cursor functionality is not supported in Django's built-in search
        }