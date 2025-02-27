'''
Created on 06-10-2011

@author: klangner
'''

from src.lorepo.mycontent.models import Content
from search.core import porter_stemmer
import search

search.register(Content, ('title', 'tags','description', ), indexer=porter_stemmer)