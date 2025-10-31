import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'song_recommender.settings')
django.setup()

from django.contrib.auth.models import User

# Create superuser if it doesn't exist
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: username=admin, password=admin123')
else:
    print('Superuser already exists')

# Create test user if it doesn't exist
if not User.objects.filter(username='testuser').exists():
    User.objects.create_user('testuser', 'test@example.com', 'test123')
    print('Test user created: username=testuser, password=test123')
else:
    print('Test user already exists')

