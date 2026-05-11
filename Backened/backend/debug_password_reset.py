import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobilemechanic.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from users.models import PasswordResetToken
import secrets

User = get_user_model()

# Create a test user
user = User.objects.create_user(
    phone_number='+923001234567',
    email='test@example.com',
    password='TestPass123!'
)

# Create a password reset token
token_str = secrets.token_urlsafe(32)
token = PasswordResetToken.objects.create(user=user, token=token_str)

# Test the API
api_client = APIClient()
data = {
    "reset_token": str(token.token),
    "new_password": "NewSecurePass123!",
    "new_password_confirm": "NewSecurePass123!",
}

print(f"Token: {token.token}")
print(f"Data: {data}")

response = api_client.post("/api/v1/auth/reset-password/", data, format="json")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
