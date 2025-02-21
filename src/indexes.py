from dbindexer import autodiscover
autodiscover()

# search for "search_indexes.py" in all installed apps
from . import search
search.autodiscover()

from . import autoload
autoload.autodiscover("signals")