import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# Import models
from django.contrib.auth.models import User
from mainapp.models import UserProfile

# Get the first superuser
superuser = User.objects.filter(is_superuser=True).first()

if superuser:
    # Update email to deeplogicai.tech domain if needed
    if not superuser.email.endswith('@deeplogicai.tech'):
        username = superuser.username.lower()
        superuser.email = f"{username}@deeplogicai.tech"
        superuser.save()
        print(f"Updated email to {superuser.email}")
    
    # Create or update UserProfile with ADMIN role
    profile, created = UserProfile.objects.get_or_create(user=superuser)
    profile.role = UserProfile.ADMIN
    profile.save()
    
    print(f"User '{superuser.username}' has been set to ADMIN role.")
    print(f"Email: {superuser.email}")
else:
    print("No superuser found.")
