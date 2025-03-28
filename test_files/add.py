import os
import django
import sys
from google.cloud import datastore


# Set up Django
sys.path.append("D:/Smart Education/Projects/eauther")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.settings")
django.setup()


client = datastore.Client()
kind = "auth_user"
user_key = client.key(kind)

user = datastore.Entity(user_key)

user = datastore.Entity(user_key)
user.update({
    "username": "john_doe",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "is_staff": False,
    "is_active": True,
    "is_superuser": False,
    "date_joined": None,  # Datastore doesn't support SERVER_TIMESTAMP
    "last_login": None,
    "password": "hashed_password_here"
})

# client.put(user)
# print(f"Created user with ID: {user.key.id}")


def add_profile(user_id):
    profile_key = client.key("profile", user_id)  # Use user_id as the key

    profile = datastore.Entity(profile_key)
    profile.update({
        "bio": "Software Developer",
        "location": "Cairo, Egypt",
        "website": "https://example.com"
    })

    client.put(profile)
    print(f"Profile created for User ID: {user_id}")

# Example: Add profile for user with his ID
add_profile(1)