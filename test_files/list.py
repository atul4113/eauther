import os
import django
import sys
from google.cloud import datastore
import datetime


# Set up Django
sys.path.append("D:/Smart Education/Projects/eauther")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.settings")  
django.setup()

# os.environ["DATASTORE_EMULATOR_HOST"] = "localhost:8081"  # Adjust port if needed
# os.environ["DATASTORE_PROJECT_ID"] = "your-project-id"

client = datastore.Client()

def list_users():
    query = client.query(kind="auth_user")
    users = list(query.fetch())
    print('list_users function started ..')
    for user in users:
        print(f"ID: {user.key.id}, Username: {user['username']}, Email: {user['email']}")

list_users()

def list_profiles():
    query = client.query(kind="profile")
    profiles = list(query.fetch())

    for profile in profiles:
        print(f"ID: {profile.key.id}")
        for key, value in profile.items():
            print(f"{key}: {value}")
        print("-" * 20)

# list_profiles()

def get_user_with_profile(user_id):
    user_key = client.key("auth_user", user_id)
    profile_key = client.key("profile", user_id)  # Use the same user_id for profile key

    user = client.get(user_key)
    profile = client.get(profile_key)

    if user:
        print(f"User: {user['username']}, Email: {user['email']}")
        if profile:
            print(f"Profile: Activation Key: {profile['activation_key']}, Is Active: {profile.get('is_active', 'Not specified')}")
        else:
            print("No profile found for this user.")
    else:
        print("User not found.")

# get_user_with_profile(9)


def list_kinds():
    query = client.query(kind="__kind__")
    kinds = list(query.fetch())

    for kind in kinds:
        print(kind.key.name)

# list_kinds()


def list_django_users():
    print("\nQuerying users via Django ORM:")
    from django.contrib.auth.models import User
    users = User.objects.all()
    
    print(f"Found {len(users)} users via Django ORM:")
    for user in users:
        print(f"  ID: {user.id}, Username: {user.username}, Email: {user.email}")
        print(f"  Is active: {user.is_active}, Date joined: {user.date_joined}")


list_django_users()


def list_users_2():
    # Try multiple possible kind names
    possible_kinds = ["auth_user", "django_user", "django_contrib_auth_user", "User", "company_user"]
    
    for kind in possible_kinds:
        print(f"\nAttempting to query kind: {kind}")
        query = client.query(kind=kind)
        users = list(query.fetch())
        
        if users:
            print(f"Found {len(users)} users with kind '{kind}':")
            for user in users:
                # Handle different property names
                username = user.get('username', user.get('name', 'N/A'))
                email = user.get('email', 'N/A')
                print(f"  ID: {user.key.id}, Username: {username}, Email: {email}")
                # Print all properties to debug
                print(f"  All properties: {dict(user.items())}")
        else:
            print(f"No users found with kind '{kind}'")

# list_users_2()


def find_user_entities():
    print("\nSearching for user entities in all kinds...")
    
    # First, list all kinds in the datastore
    query = client.query(kind="__kind__")
    kinds = list(query.fetch())
    
    user_related_kinds = []
    
    # Look for kinds that might be user-related
    for kind in kinds:
        kind_name = kind.key.name
        print(f"Found kind: {kind_name}")
        
        # Check for kinds with "user", "auth", or "django" in the name
        if "user" in kind_name.lower() or "auth" in kind_name.lower() or "django" in kind_name.lower():
            user_related_kinds.append(kind_name)
    
    # Query each potential user kind to find the new users
    print("\nPotential user-related kinds:", user_related_kinds)
    
    for kind_name in user_related_kinds:
        print(f"\nQuerying kind: {kind_name}")
        query = client.query(kind=kind_name)
        entities = list(query.fetch(limit=10))
        
        print(f"Found {len(entities)} entities")
        
        # Check each entity for user-like properties
        for entity in entities:
            properties = dict(entity.items())
            
            # Check if this has username or email properties
            if "username" in properties or "email" in properties:
                print(f"  Found potential user entity in kind '{kind_name}':")
                print(f"  Key: {entity.key}")
                print(f"  Properties: {properties}")

# find_user_entities()

def create_test_user_directly():
    print("\nCreating a test user directly in Datastore...")
    
    # Create a new user entity
    user_key = client.key("auth_user")  # Let Datastore assign an ID
    user = datastore.Entity(key=user_key)
    
    # Set user properties
    user.update({
        'username': 'direct_test_user',
        'email': 'direct@test.com',
        'password': 'test_password',
        'is_active': True,
        'first_name': 'Direct',
        'last_name': 'Test',
        'is_staff': False,
        'is_superuser': False,
        'date_joined': datetime.datetime.now(),
        'last_login': None
    })
    
    # Save the entity
    client.put(user)
    print(f"Created user with key: {user.key}")
    
    # Verify it exists
    saved_user = client.get(user.key)
    if saved_user:
        print(f"Successfully retrieved user: {saved_user['username']}")
    else:
        print("Failed to retrieve the user")

# create_test_user_directly()

def list_all_users_with_profiles():
    """
    List all users and their profiles from both Django ORM and Datastore.
    """
    print("\nListing all users with profiles:")
    
    # Get all users from Django ORM
    from django.contrib.auth.models import User
    django_users = User.objects.all()
    
    # Get all profiles from Datastore
    query = client.query(kind="profile")
    datastore_profiles = list(query.fetch())
    
    # Create a mapping of user IDs to profiles
    profile_map = {profile['user_id']: profile for profile in datastore_profiles}
    
    # Print all users and their profiles
    for user in django_users:
        print(f"\nUser ID: {user.id}")
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"Is Active: {user.is_active}")
        
        # Get profile from Datastore
        profile = profile_map.get(user.id)
        if profile:
            print("Profile found in Datastore:")
            print(f"  Activation Key: {profile['activation_key']}")
            print(f"  Is Active: {profile.get('is_active', 'Not specified')}")
        else:
            print("No profile found in Datastore")
        
        # Get profile from Django ORM
        try:
            django_profile = user.registrationprofile
            print("Profile found in Django ORM:")
            print(f"  Activation Key: {django_profile.activation_key}")
        except:
            print("No profile found in Django ORM")

# list_all_users_with_profiles()