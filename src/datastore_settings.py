from gcloudc.db.backends.datastore import DATASTORE_SETTINGS

# Configure gcloudc to avoid transaction issues
DATASTORE_SETTINGS.update({
    'DISABLE_CONSTRAINT_CHECKS': True,
    'DISABLE_TRANSACTION_ENFORCEMENT': True,
    'ENFORCE_ENTITY_EXISTENCE': False,
    'ENTITY_EXISTENCE_TIMEOUT': 30  # seconds
})