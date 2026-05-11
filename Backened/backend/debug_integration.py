import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobilemechanic.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.core.cache import cache

User = get_user_model()

api_client = APIClient()

# Step 1: Signup
signup_data = {
    "phone_number": "+923001234568",
    "email": "test2@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
}
response = api_client.post("/api/v1/auth/signup/", signup_data, format="json")
print(f"Signup: {response.status_code}")

# Step 2: Login
login_data = {"phone_number": "+923001234568", "password": "SecurePass123!"}
response = api_client.post("/api/v1/auth/login/", login_data, format="json")
print(f"Login: {response.status_code}")
temp_token = response.json().get("temp_token")

# Step 3: Send OTP
otp_data = {"phone_number": "+923001234568"}
response = api_client.post("/api/v1/auth/send-otp/", otp_data, format="json")
print(f"Send OTP: {response.status_code}")

# Step 4: Verify OTP
user = User.objects.get(phone_number="+923001234568")
otp_code = cache.get(f"otp_{user.id}")
print(f"Cache key otp_{user.id}: {otp_code}")
otp_code = cache.get(f"otp_code_{user.phone_number}")
print(f"Cache key otp_code_{user.phone_number}: {otp_code}")

# Try to verify with the actual cache key
if otp_code:
    verify_data = {"phone_number": "+923001234568", "otp": otp_code}
    response = api_client.post("/api/v1/auth/verify-otp/", verify_data, format="json")
    print(f"Verify OTP (with correct key): {response.status_code}")
    print(f"Response: {response.json()}")
else:
    print("No OTP in cache")
    # Try with "123456"
    verify_data = {"phone_number": "+923001234568", "otp": "123456"}
    response = api_client.post("/api/v1/auth/verify-otp/", verify_data, format="json")
    print(f"Verify OTP (with 123456): {response.status_code}")
    print(f"Response: {response.json()}")
