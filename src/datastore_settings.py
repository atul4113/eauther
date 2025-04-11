from gcloudc.db.backends.datastore import DATASTORE_SETTINGS

# Configure gcloudc to avoid transaction issues
DATASTORE_SETTINGS.update({
    'NAMESPACE': '',  # Using default namespace
    'PROJECT': 'eauthor-dev',  # Correct project ID
    'DISABLE_CONSTRAINT_CHECKS': True,  # Match DJANGAE_DISABLE_CONSTRAINT_CHECKS
    'DISABLE_TRANSACTION_ENFORCEMENT': False,
    'HIGH_REPLICATION': True,
    'EVENTUAL_CONSISTENCY_PROBABILITY': 1.0,  # Always use eventual consistency
    'CREATE_TRANSACTION_COMMIT_ON_COMPLETION': True,  # Force transactions to commit
})