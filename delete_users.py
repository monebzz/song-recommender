import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'song_recommender.settings')
django.setup()

from django.contrib.auth.models import User
from recommender.models import UserProfile

print("=" * 50)
print("DELETING ALL USER ACCOUNTS")
print("=" * 50)

# Get counts before deletion
user_count = User.objects.count()
profile_count = UserProfile.objects.count()

print(f"Found {user_count} users")
print(f"Found {profile_count} profiles")

# Delete all users (this will cascade to profiles)
User.objects.all().delete()

print("=" * 50)
print("✅ All user accounts deleted successfully!")
print("=" * 50)
