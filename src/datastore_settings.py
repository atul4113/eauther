from gcloudc.db.backends.datastore import DATASTORE_SETTINGS

# Configure gcloudc to avoid transaction issues
DATASTORE_SETTINGS.update({
    'NAMESPACE': '',  # Make sure this is empty or matches your intended namespace
    'PROJECT': 'ealpha-test-application',  # Must match your actual project ID
    'DISABLE_CONSTRAINT_CHECKS': False,
    'DISABLE_TRANSACTION_ENFORCEMENT': False,
    'HIGH_REPLICATION': True,
    'EVENTUAL_CONSISTENCY_PROBABILITY': 1.0,  # Always use eventual consistency
    'CREATE_TRANSACTION_COMMIT_ON_COMPLETION': True,  # Force transactions to commit
})