"""
Signup/Registration tests (AUTH-001 to AUTH-005)
Tests user registration with valid/invalid data, phone validation, etc.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()


@pytest.mark.django_db
class TestSignupSuccess:
    """AUTH-001: User can register with valid data"""
    
    def test_signup_with_valid_data(self, api_client, valid_signup_data):
        """Test successful signup with valid phone + email + password"""
        response = api_client.post('/api/v1/auth/signup/', valid_signup_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(phone_number=valid_signup_data['phone_number']).exists()
        assert 'user_id' in response.json()
        
    def test_signup_creates_user_with_correct_fields(self, api_client, valid_signup_data):
        """Verify all required fields are set correctly"""
        response = api_client.post('/api/v1/auth/signup/', valid_signup_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        user = User.objects.get(phone_number=valid_signup_data['phone_number'])
        assert user.email == valid_signup_data['email']
        assert user.phone_verified is False  # Not verified yet
        assert user.email_verified is False  # Not verified yet
        
    def test_signup_response_contains_required_fields(self, api_client, valid_signup_data):
        """Verify response contains necessary information"""
        response = api_client.post('/api/v1/auth/signup/', valid_signup_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert 'user_id' in data
        assert 'phone_number' in data or data.get('phone_number') == valid_signup_data['phone_number']


@pytest.mark.django_db
class TestSignupDuplicatePhone:
    """AUTH-002: User cannot register with existing phone"""
    
    def test_duplicate_phone_number_rejected(self, api_client, authenticated_user):
        """Test duplicate phone number returns 400 error"""
        user, _ = authenticated_user
        
        duplicate_data = {
            'phone_number': user.phone_number,
            'email': 'another@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
        }
        
        response = api_client.post('/api/v1/auth/signup/', duplicate_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'phone_number' in response.json() or 'detail' in response.json()
        
    def test_only_one_user_with_phone_exists(self, api_client, authenticated_user):
        """Verify only one user exists with given phone"""
        user, _ = authenticated_user
        
        duplicate_data = {
            'phone_number': user.phone_number,
            'email': 'another@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
        }
        
        api_client.post('/api/v1/auth/signup/', duplicate_data)
        
        users_count = User.objects.filter(phone_number=user.phone_number).count()
        assert users_count == 1


@pytest.mark.django_db
class TestSignupInvalidPhoneFormat:
    """AUTH-003: Reject invalid phone number format"""
    
    def test_invalid_phone_format_rejected(self, api_client):
        """Test various invalid phone formats"""
        invalid_phones = [
            '12345',  # Too short
            'abc123def456',  # Letters
            '9999999999999999',  # Too long
            '+1234',  # Too short with +
            '',  # Empty
        ]
        
        for invalid_phone in invalid_phones:
            data = {
                'phone_number': invalid_phone,
                'email': 'test@example.com',
                'password': 'SecurePass123!',
                'password_confirm': 'SecurePass123!',
            }
            
            response = api_client.post('/api/v1/auth/signup/', data)
            assert response.status_code == status.HTTP_400_BAD_REQUEST, f"Phone {invalid_phone} should be rejected"
            
    def test_valid_international_formats_accepted(self, api_client):
        """Test valid international phone formats are accepted"""
        valid_phones = [
            '+923001234567',  # Pakistan format
            '+14155552671',   # US format
            '+441632960000',  # UK format
        ]
        
        for idx, valid_phone in enumerate(valid_phones):
            data = {
                'phone_number': valid_phone,
                'email': f'test{idx}@example.com',
                'password': 'SecurePass123!',
                'password_confirm': 'SecurePass123!',
            }
            
            response = api_client.post('/api/v1/auth/signup/', data)
            assert response.status_code == status.HTTP_201_CREATED, f"Phone {valid_phone} should be accepted"


@pytest.mark.django_db
class TestSignupWeakPassword:
    """AUTH-004: Reject weak password"""
    
    def test_weak_password_rejected(self, api_client):
        """Test various weak password scenarios"""
        weak_passwords = [
            ('123456', 'Too short'),
            ('password', 'No numbers'),
            ('12345678', 'No letters'),
            ('Pass123', 'Too short'),
        ]
        
        for weak_pass, reason in weak_passwords:
            data = {
                'phone_number': '+923001234567',
                'email': 'test@example.com',
                'password': weak_pass,
                'password_confirm': weak_pass,
            }
            
            response = api_client.post('/api/v1/auth/signup/', data)
            assert response.status_code == status.HTTP_400_BAD_REQUEST, f"{reason} should be rejected"
            
    def test_password_mismatch_rejected(self, api_client):
        """Test password and confirm password mismatch"""
        data = {
            'phone_number': '+923001234567',
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'DifferentPass123!',
        }
        
        response = api_client.post('/api/v1/auth/signup/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestSignupEmptyFields:
    """AUTH-005: Reject empty request"""
    
    def test_empty_request_rejected(self, api_client):
        """Test empty POST data"""
        response = api_client.post('/api/v1/auth/signup/', {})
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
    def test_missing_phone_rejected(self, api_client):
        """Test missing phone number"""
        data = {
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
        }
        
        response = api_client.post('/api/v1/auth/signup/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
    def test_missing_email_rejected(self, api_client):
        """Test missing email"""
        data = {
            'phone_number': '+923001234567',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
        }
        
        response = api_client.post('/api/v1/auth/signup/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
    def test_missing_password_rejected(self, api_client):
        """Test missing password"""
        data = {
            'phone_number': '+923001234567',
            'email': 'test@example.com',
        }
        
        response = api_client.post('/api/v1/auth/signup/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
    def test_invalid_email_format_rejected(self, api_client):
        """Test invalid email format"""
        invalid_emails = [
            'notanemail',
            'missing@domain',
            '@example.com',
            'test@',
        ]
        
        for invalid_email in invalid_emails:
            data = {
                'phone_number': '+923001234567',
                'email': invalid_email,
                'password': 'SecurePass123!',
                'password_confirm': 'SecurePass123!',
            }
            
            response = api_client.post('/api/v1/auth/signup/', data)
            assert response.status_code == status.HTTP_400_BAD_REQUEST, f"Email {invalid_email} should be rejected"
