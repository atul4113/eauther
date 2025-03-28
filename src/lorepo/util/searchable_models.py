import logging
import re
import traceback
from django.db import models
from djangae.contrib.search import document, index
from src.libraries.utility.environment import get_versioned_module
from src.libraries.utility.queues import trigger_backend_task, TaskQueue


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
        super().save(*args, **kwargs)
        if hasattr(self, '_search_indexed_fields'):
            self.add_to_search_index()

    def add_to_search_index(self):
        """Adds the object to the search index."""
        try:
            # Create a document with the indexed fields
            doc = {
                field: getattr(self, field)
                for field in self._search_indexed_fields
                if hasattr(self, field)
            }
            document.create_document(self._meta.model_name, str(self.id), doc)
        except Exception as e:
            logging.error(f"Failed to add to search index: {e}")
            logging.error(traceback.format_exc())
            self.save_search_index_in_backend()

    def remove_from_search_index(self):
        """Removes the object from the search index."""
        try:
            document.delete_document(self._meta.model_name, str(self.id))
        except Exception as e:
            logging.error(f"Failed to remove from search index: {e}")
            self.save_search_index_in_backend()

    @classmethod
    def search(cls, term, cursor_string=None, limit=20, **kwargs):
        """
        Searches for objects matching the given term.
        """
        if not term:
            return {'number_found': 0, 'results': [], 'cursor': None}

        try:
            results = index.search(
                term,
                model_name=cls._meta.model_name,
                limit=limit
            )
            return {
                'number_found': len(results),
                'results': [cls.objects.get(pk=result.doc_id.split('__')[-1]) for result in results],
                'cursor': None
            }
        except Exception as e:
            logging.error(f"Search failed: {e}")
            return {'number_found': 0, 'results': [], 'cursor': None}

    def tokenize_phrase(self, phrase, start_word=2):
        """Tokenizes a phrase for search indexing."""
        tokens = set()
        for word in phrase.split():
            for i in range(1, len(word) + 1):
                if i > start_word:
                    tokens.add(word[0:i])
        return ' '.join(tokens)

    def tokenized_value(self, field):
        """Returns a tokenized value for a given field."""
        text = str(getattr(self, field, ""))
        text = re.sub(r"[\,;\/\-\(\)\!#$%\^\&\*=\|]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return self.tokenize_phrase(text)


class Indexable(SearchableModel):
    """
    Abstract model that supports indexing in a search engine.
    """
    def save(self, *args, **kwargs):
        # Save data only in the full-text search engine
        if hasattr(self, '_search_indexed_fields'):
            self.add_to_search_index()

    @classmethod
    def search(cls, query, page=1, limit=10, **kwargs):
        """
        Searches for objects matching the given query.
        """
        if not query:
            return {'number_found': 0, 'results': [], 'cursor': None}

        try:
            results = index.search(
                query,
                model_name=cls._meta.model_name,
                offset=(page - 1) * limit,
                limit=limit
            )
            return {
                'number_found': len(results),
                'results': [cls.objects.get(pk=result.doc_id.split('__')[-1]) for result in results],
                'cursor': None
            }
        except Exception as e:
            logging.error(f"Search failed: {e}")
            return {'number_found': 0, 'results': [], 'cursor': None}