# __init__.py
from .celery import app as celery_app

__all__ = ('celery_app',)


try:
    from .patches import *  # Apply patches when app is loaded
except ImportError:
    pass


try:
    from .datastore_patches import *
except ImportError:
    pass