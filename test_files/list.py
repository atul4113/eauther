import os
import django
import sys
from google.cloud import datastore


# Set up Django
sys.path.append("D:/Smart Education/Projects/eauther")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.settings")  
django.setup()


client = datastore.Client()

def list_users():
    query = client.query(kind="auth_user")
    users = list(query.fetch())

    for user in users:
        print(f"ID: {user.key.id}, Username: {user['username']}, Email: {user['email']}")

list_users()


def get_user_with_profile(user_id):
    user_key = client.key("auth_user", user_id)
    profile_key = client.key("profile", user_id)

    user = client.get(user_key)
    profile = client.get(profile_key)

    if user:
        print(f"User: {user['username']}, Email: {user['email']}")
        if profile:
            print(f"Profile: {profile['bio']}, Location: {profile['location']}")
        else:
            print("No profile found for this user.")
    else:
        print("User not found.")

get_user_with_profile(1)


def list_kinds():
    query = client.query(kind="__kind__")
    kinds = list(query.fetch())

    for kind in kinds:
        print(kind.key.name)

list_kinds()


def list_django_users():
    print("\nQuerying users via Django ORM:")
    from django.contrib.auth.models import User
    users = User.objects.all()
    
    print(f"Found {len(users)} users via Django ORM:")
    for user in users:
        print(f"  ID: {user.id}, Username: {user.username}, Email: {user.email}")
        print(f"  Is active: {user.is_active}, Date joined: {user.date_joined}")


list_django_users()
