from google.cloud import datastore
from gcloudc.db.backends.datastore import DATASTORE_SETTINGS
from django.db.models.signals import post_save
from django.contrib.auth.models import User

# Update Datastore settings to ensure data is persisted
DATASTORE_SETTINGS.update({
    'CREATE_TRANSACTION_COMMIT_ON_COMPLETION': True,
    'HIGH_REPLICATION': True,
    'EVENTUAL_CONSISTENCY_PROBABILITY': 1.0,
    'DISABLE_CONSTRAINT_CHECKS': True,  # Only if needed
})

# Create a function to manually persist users to Datastore
def ensure_user_persisted(sender, instance, created, **kwargs):
    """
    When a User model is saved, ensure it's properly persisted to Datastore
    by doing a direct write if needed.
    """
    if created:  # Only for newly created users
        print(f"Ensuring user {instance.username} is persisted to Datastore...")
        
        # Create a direct Datastore client
        client = datastore.Client()
        
        # Create entity with the same ID that Django assigned
        user_key = client.key("auth_user", instance.id)
        
        # Check if it already exists
        existing = client.get(user_key)
        if not existing:
            # Create the entity
            entity = datastore.Entity(key=user_key)
            
            # Copy relevant user properties
            entity.update({
                'username': instance.username,
                'email': instance.email,
                'password': instance.password,
                'first_name': instance.first_name,
                'last_name': instance.last_name,
                'is_active': instance.is_active,
                'is_staff': instance.is_staff,
                'is_superuser': instance.is_superuser,
                'date_joined': instance.date_joined,
                'last_login': instance.last_login
            })
            
            # Save the entity directly to Datastore
            client.put(entity)
            print(f"User {instance.username} was manually persisted to Datastore")

# Connect the signal handler
post_save.connect(ensure_user_persisted, sender=User)