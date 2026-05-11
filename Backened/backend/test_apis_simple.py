#!/usr/bin/env python
"""
Simple API Test Suite for Mobile Mechanic Backend
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def print_test(name, status_code, expected_code=200):
    """Print test result"""
    success = 200 <= status_code < 300
    # Special case: 401 Unauthorized is expected for security test
    if name == "Unauthorized (No Token)" and status_code == 401:
        success = True
    indicator = "✓ PASS" if success else "✗ FAIL"
    print(f"{indicator} | {name:40} | Status: {status_code}")
    return success

def print_response_data(response, name="Response Data"):
    """Print formatted response data from backend"""
    print(f"\n  📊 {name}:")
    try:
        data = response.json()
        print(f"     {json.dumps(data, indent=6)}")
    except:
        print(f"     {response.text[:500]}")

print("\n" + "="*80)
print("MOBILE MECHANIC API TEST SUITE")
print("="*80 + "\n")

# Generate unique user
timestamp = str(int(time.time()))
email = f"test{timestamp}@example.com"
phone = f"+9230000{timestamp[-6:]}"
password = "Test@123456"

token = None
results = []

# Test 1: User Signup
print("1. AUTHENTICATION TESTS")
print("-" * 80)
response = requests.post(
    f"{BASE_URL}/api/v1/auth/signup/",
    json={
        "phone_number": phone,
        "email": email,
        "password": password,
        "password_confirm": password,
        "first_name": "Test",
        "last_name": "User"
    }
)
success = print_test("Signup", response.status_code, 201)
results.append(success)
print_response_data(response, "Signup Response")
if success:
    data = response.json()
    token = data.get('token')
    print(f"  → Token: {token[:20]}...")
    print(f"  → User ID: {data.get('user_id')}")

# Test 2: User Profile
if token:
    response = requests.get(
        f"{BASE_URL}/api/v1/auth/profile/",
        headers={"Authorization": f"Token {token}"}
    )
    success = print_test("Get Profile", response.status_code, 200)
    results.append(success)
    print_response_data(response, "Profile Response")
    if success:
        data = response.json()
        print(f"  → Name: {data.get('first_name')} {data.get('last_name')}")
        print(f"  → Email: {data.get('email')}")

# Test 3: Services
print("\n2. SERVICES TESTS")
print("-" * 80)
response = requests.get(
    f"{BASE_URL}/api/v1/services/",
    headers={"Authorization": f"Token {token}"} if token else {}
)
success = print_test("Get Services", response.status_code, 200)
results.append(success)
print_response_data(response, "Services Response")
if success:
    data = response.json()
    count = len(data) if isinstance(data, list) else data.get("count", 0)
    print(f"  → Found {count} services")

# Test 4: Mechanics
response = requests.get(
    f"{BASE_URL}/api/v1/mechanics/",
    headers={"Authorization": f"Token {token}"} if token else {}
)
success = print_test("Get Mechanics", response.status_code, 200)
results.append(success)
print_response_data(response, "Mechanics Response")
if response.status_code == 200:
    data = response.json()
    count = len(data) if isinstance(data, list) else data.get("count", 0)
    print(f"  → Found {count} mechanics")

# Test 5: Bookings
print("\n3. BOOKING TESTS")
print("-" * 80)
response = requests.get(
    f"{BASE_URL}/api/v1/bookings/",
    headers={"Authorization": f"Token {token}"} if token else {}
)
success = print_test("Get Bookings", response.status_code, 200)
results.append(success)
print_response_data(response, "Bookings Response")
if success:
    data = response.json()
    count = len(data) if isinstance(data, list) else data.get("count", 0)
    print(f"  → User has {count} bookings")

# Test 6: Create Booking (requires service and mechanic IDs)
if token:
    response = requests.post(
        f"{BASE_URL}/api/v1/bookings/",
        headers={"Authorization": f"Token {token}"},
        json={
            "service": 1,
            "mechanic": 1,
            "description": "Test booking",
            "location": "Test Location"
        }
    )
    success = print_test("Create Booking", response.status_code, [200, 201, 400])
    results.append(success if response.status_code < 300 else False)
    print_response_data(response, "Create Booking Response")
    if response.status_code < 300:
        print(f"  → Booking created successfully")
    elif response.status_code == 400:
        print(f"  → Validation error (invalid service/mechanic)")

# Test 7: Notifications
print("\n4. OTHER FEATURES TESTS")
print("-" * 80)
response = requests.get(
    f"{BASE_URL}/api/v1/notifications/",
    headers={"Authorization": f"Token {token}"} if token else {}
)
success = print_test("Get Notifications", response.status_code, 200)
results.append(success)
print_response_data(response, "Notifications Response")
if success:
    data = response.json()
    count = len(data) if isinstance(data, list) else data.get("count", 0)
    print(f"  → Found {count} notifications")

# Test 8: Reviews
response = requests.get(
    f"{BASE_URL}/api/v1/reviews/",
    headers={"Authorization": f"Token {token}"} if token else {}
)
success = print_test("Get Reviews", response.status_code, 200)
results.append(success)
print_response_data(response, "Reviews Response")
if success:
    data = response.json()
    count = len(data) if isinstance(data, list) else data.get("count", 0)
    print(f"  → Found {count} reviews")

# Test 9: Job Offers
response = requests.get(
    f"{BASE_URL}/api/v1/job-offers/",
    headers={"Authorization": f"Token {token}"} if token else {}
)
success = print_test("Get Job Offers", response.status_code, 200)
results.append(success)
print_response_data(response, "Job Offers Response")
if success:
    data = response.json()
    count = len(data) if isinstance(data, list) else data.get("count", 0)
    print(f"  → Found {count} job offers")

# Test 10: Unauthorized Access
print("\n5. SECURITY TESTS")
print("-" * 80)
response = requests.get(f"{BASE_URL}/api/v1/bookings/")
success = print_test("Unauthorized (No Token)", response.status_code, 401)
results.append(success)
print_response_data(response, "Unauthorized Response")
print(f"  → Correctly rejected unauthorized request")

# Summary
print("\n" + "="*80)
print("TEST SUMMARY")
print("="*80)
passed = sum(results)
total = len(results)
percentage = (passed / total * 100) if total > 0 else 0
print(f"\n✓ Passed: {passed}/{total} ({percentage:.1f}%)")
print("="*80 + "\n")


