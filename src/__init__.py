import os
from django.db import connections

# Force non-transactional mode when app loads
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
connections['default'].settings_dict['OPTIONS']['use_transactions'] = False

# Monkey-patch to prevent transaction usage
from django.db import transaction
transaction.atomic = lambda using=None: (item for item in (None,))  # Disables all transactions