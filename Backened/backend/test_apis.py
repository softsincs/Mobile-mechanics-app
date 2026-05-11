#!/usr/bin/env python
"""
Comprehensive API Test Suite for Mobile Mechanic Backend
Tests all endpoints with various scenarios
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

class APITester:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_token = None
        self.refresh_token = None
        self.user_id = None
        
    def print_response(self, name: str, response: requests.Response):
        """Print formatted response"""
        status_indicator = "✓ PASS" if 200 <= response.status_code < 300 else "✗ FAIL"
        print(f"\n{'='*80}")
        print(f"{status_indicator} - {name}")
        print(f"{'='*80}")
        print(f"Status Code: {response.status_code}")
        try:
            resp_json = response.json()
            print(f"Response:\n{json.dumps(resp_json, indent=2)}")
        except:
            print(f"Response:\n{response.text[:500]}")
        print()

    def test_signup(self):
        """Test User Registration"""
        url = f"{self.base_url}/api/v1/auth/signup/"
        import time
        phone = f"+9230012345{int(time.time()) % 100:02d}"  # Generate unique phone
        payload = {
            "phone_number": phone,
            "email": f"testuser{int(time.time())}@example.com",
            "password": "TestPassword123!",
            "password_confirm": "TestPassword123!",
            "first_name": "Test",
            "last_name": "User"
        }
        response = self.session.post(url, json=payload)
        self.print_response("SIGNUP - Success", response)
        
        if response.status_code in [200, 201]:
            data = response.json()
            self.user_id = data.get('id') or data.get('user_id')
            # Try different token field names
            if 'access' in data:
                self.auth_token = data['access']
            elif 'token' in data:
                self.auth_token = data['token']
            if 'refresh' in data:
                self.refresh_token = data['refresh']
        
        return response.status_code

    def test_login(self):
        """Test User Login"""
        url = f"{self.base_url}/api/v1/auth/login/"
        payload = {
            "email": "testuser@example.com",
            "password": "TestPassword123!"
        }
        response = self.session.post(url, json=payload)
        self.print_response("LOGIN - Success", response)
        
        if response.status_code in [200, 201]:
            data = response.json()
            # Try different token field names
            if 'access' in data:
                self.auth_token = data['access']
            elif 'token' in data:
                self.auth_token = data['token']
            if 'refresh' in data:
                self.refresh_token = data['refresh']
        
        return response.status_code

    def test_get_services(self):
        """Test Get All Services"""
        url = f"{self.base_url}/api/v1/services/"
        headers = self._get_auth_headers()
        response = self.session.get(url, headers=headers)
        self.print_response("GET SERVICES - List All", response)
        return response.status_code

    def test_get_mechanics(self):
        """Test Get All Mechanics"""
        url = f"{self.base_url}/api/v1/mechanics/"
        headers = self._get_auth_headers()
        response = self.session.get(url, headers=headers)
        self.print_response("GET MECHANICS - List All", response)
        return response.status_code

    def test_create_booking(self):
        """Test Create Booking"""
        url = f"{self.base_url}/api/v1/bookings/"
        headers = self._get_auth_headers()
        payload = {
            "service_id": 1,
            "mechanic_id": 1,
            "description": "Car maintenance needed",
            "location": "123 Main St, City",
            "phone_number": "+923001234567"
        }
        response = self.session.post(url, json=payload, headers=headers)
        self.print_response("CREATE BOOKING - Success", response)
        return response.status_code

    def test_get_bookings(self):
        """Test Get User Bookings"""
        url = f"{self.base_url}/api/v1/bookings/"
        headers = self._get_auth_headers()
        response = self.session.get(url, headers=headers)
        self.print_response("GET BOOKINGS - List User", response)
        return response.status_code

    def test_get_ratings(self):
        """Test Get Ratings"""
        url = f"{self.base_url}/api/v1/ratings/"
        headers = self._get_auth_headers()
        response = self.session.get(url, headers=headers)
        self.print_response("GET RATINGS", response)
        return response.status_code

    def test_get_notifications(self):
        """Test Get Notifications"""
        url = f"{self.base_url}/api/v1/notifications/"
        headers = self._get_auth_headers()
        response = self.session.get(url, headers=headers)
        self.print_response("GET NOTIFICATIONS", response)
        return response.status_code

    def test_get_analytics(self):
        """Test Get Analytics"""
        url = f"{self.base_url}/api/v1/analytics/"
        headers = self._get_auth_headers()
        response = self.session.get(url, headers=headers)
        self.print_response("GET ANALYTICS", response)
        return response.status_code

    def test_get_dispatch(self):
        """Test Get Dispatch"""
        url = f"{self.base_url}/api/v1/dispatch/"
        headers = self._get_auth_headers()
        response = self.session.get(url, headers=headers)
        self.print_response("GET DISPATCH", response)
        return response.status_code

    def test_unauthorized(self):
        """Test Unauthorized Access"""
        url = f"{self.base_url}/api/v1/bookings/"
        response = self.session.get(url)  # No auth headers
        self.print_response("UNAUTHORIZED - No Token", response)
        return response.status_code

    def _get_auth_headers(self):
        """Get authorization headers"""
        if self.auth_token:
            return {"Authorization": f"Token {self.auth_token}"}
        return {}

    def run_all_tests(self):
        """Run all API tests"""
        print("\n" + "="*80)
        print("MOBILE MECHANIC - API TEST SUITE")
        print("="*80)
        
        results = {}
        
        # Auth Tests
        results['Signup'] = self.test_signup()
        results['Login'] = self.test_login()
        results['Unauthorized'] = self.test_unauthorized()
        
        # Service Tests
        results['Get Services'] = self.test_get_services()
        results['Get Mechanics'] = self.test_get_mechanics()
        
        # Booking Tests
        results['Create Booking'] = self.test_create_booking()
        results['Get Bookings'] = self.test_get_bookings()
        
        # Other Tests
        results['Get Ratings'] = self.test_get_ratings()
        results['Get Notifications'] = self.test_get_notifications()
        results['Get Analytics'] = self.test_get_analytics()
        results['Get Dispatch'] = self.test_get_dispatch()
        
        # Summary
        self._print_summary(results)
        
    def _print_summary(self, results: Dict[str, int]):
        """Print test summary"""
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        success_count = 0
        for test_name, status_code in results.items():
            status = "✓ PASS" if 200 <= status_code < 300 else "✗ FAIL"
            if 200 <= status_code < 300:
                success_count += 1
            print(f"{status} - {test_name}: {status_code}")
        
        print(f"\nTotal: {success_count}/{len(results)} tests passed")
        print("="*80 + "\n")

if __name__ == "__main__":
    tester = APITester()
    tester.run_all_tests()
