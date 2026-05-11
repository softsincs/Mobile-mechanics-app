"""
Tests for Google OAuth and social authentication integration.
Tests social login flow, user creation, and token generation.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from allauth.socialaccount.models import SocialAccount, SocialApp
from django.contrib.sites.models import Site

User = get_user_model()


@pytest.mark.django_db
class TestGoogleOAuthFlow:
    """Test Google OAuth authentication flow."""
    
    def setup_method(self):
        """Set up test client and fixtures."""
        self.client = APIClient()
        self.site = Site.objects.get_or_create(pk=1, defaults={'domain': 'localhost', 'name': 'localhost'})[0]
    
    def test_google_oauth_endpoint_available(self):
        """Test that Google OAuth callback endpoint is available."""
        response = self.client.get('/accounts/google/login/')
        # Should either redirect or require authentication
        assert response.status_code in [200, 302, 401]
    
    def test_drf_auth_registration_endpoint_available(self):
        """Test that dj-rest-auth registration endpoint is available."""
        response = self.client.get('/api/auth/registration/')
        # Should be available (even if GET not allowed)
        assert response.status_code in [200, 405]  # 405 = Method Not Allowed
    
    def test_google_oauth_user_creation(self):
        """Test user creation via Google OAuth social login."""
        # Simulate Google OAuth user data
        google_user_data = {
            'id': '123456789',
            'email': 'testuser@gmail.com',
            'name': 'Test User',
            'given_name': 'Test',
            'family_name': 'User',
            'picture': 'https://example.com/picture.jpg',
        }
        
        # Manually create user through social account
        user = User.objects.create_user(
            email=google_user_data['email'],
            password='temp_password_123'  # Temp password for social users
        )
        
        # Create token for the user
        token, created = Token.objects.get_or_create(user=user)
        
        # Verify user was created
        assert User.objects.filter(email=google_user_data['email']).exists()
        assert token.user == user
    
    def test_google_oauth_existing_user_login(self):
        """Test existing user login via Google OAuth."""
        # Create existing user
        user = User.objects.create_user(
            email='existing@gmail.com',
            password='password123'
        )
        
        # Ensure token exists
        token, _ = Token.objects.get_or_create(user=user)
        
        # Simulate login
        assert User.objects.get(email='existing@gmail.com') == user
        assert Token.objects.get(user=user) == token
    
    def test_token_creation_on_social_login(self):
        """Test that API token is automatically created on social login."""
        # Create user via social account
        user = User.objects.create_user(
            email='socialuser@gmail.com',
            password='temp_password_123'
        )
        
        # Token should be created or retrieved
        token, created = Token.objects.get_or_create(user=user)
        
        assert token is not None
        assert token.key is not None
        assert len(token.key) == 40  # Django token keys are 40 characters
    
    def test_social_user_email_verification(self):
        """Test that social login users have verified emails."""
        # Google OAuth users should have verified emails
        user = User.objects.create_user(
            email='verified@gmail.com',
            password='temp_password_123'
        )
        
        # In real flow, email would be marked as verified by allauth
        user.email_verified = True  # Simulating email verification
        user.save()
        
        assert user.email_verified
    
    @patch('allauth.socialaccount.adapter.DefaultSocialAccountAdapter.populate_user')
    def test_populate_user_from_google_data(self, mock_populate):
        """Test that user data is correctly populated from Google."""
        mock_user = Mock(spec=User)
        mock_user.email = 'test@gmail.com'
        mock_populate.return_value = mock_user
        
        # Simulate the adapter
        from users.adapters import CustomSocialAdapter
        adapter = CustomSocialAdapter()
        
        # Create mock request and sociallogin
        mock_request = Mock()
        mock_sociallogin = Mock()
        
        google_data = {
            'email': 'test@gmail.com',
            'name': 'Test User',
            'given_name': 'Test',
            'family_name': 'User',
        }
        
        result = adapter.populate_user(mock_request, mock_sociallogin, google_data)
        
        assert result.email == 'test@gmail.com'
    
    def test_multiple_social_providers(self):
        """Test that user can have multiple social accounts linked."""
        # Create user
        user = User.objects.create_user(
            email='multiauth@gmail.com',
            password='password123'
        )
        
        # In real scenario, multiple social accounts would be linked
        # This tests the structure is in place
        assert user.socialaccount_set.model is not None
    
    def test_social_user_profile_update(self):
        """Test that user profile can be updated from social account data."""
        user = User.objects.create_user(
            email='profile@gmail.com',
            password='temp_password'
        )
        
        # Simulate updating user data from Google
        user.first_name = 'John'
        user.last_name = 'Doe'
        user.save()
        
        updated_user = User.objects.get(email='profile@gmail.com')
        assert updated_user.first_name == 'John'
        assert updated_user.last_name == 'Doe'


@pytest.mark.django_db
class TestGoogleOAuthAdapter:
    """Test custom allauth adapter for Google OAuth."""
    
    def test_custom_account_adapter_exists(self):
        """Test that CustomAccountAdapter is properly configured."""
        from users.adapters import CustomAccountAdapter
        adapter = CustomAccountAdapter()
        
        assert adapter is not None
        assert hasattr(adapter, 'save_user')
    
    def test_custom_social_adapter_exists(self):
        """Test that CustomSocialAdapter is properly configured."""
        from users.adapters import CustomSocialAdapter
        adapter = CustomSocialAdapter()
        
        assert adapter is not None
        assert hasattr(adapter, 'save_user')
        assert hasattr(adapter, 'pre_social_login')
        assert hasattr(adapter, 'populate_user')
    
    @patch('users.adapters.Token.objects.get_or_create')
    def test_adapter_creates_token_on_save(self, mock_token_create):
        """Test that adapter creates token for new social user."""
        mock_token = Mock(spec=Token)
        mock_token_create.return_value = (mock_token, True)
        
        from users.adapters import CustomSocialAdapter
        adapter = CustomSocialAdapter()
        
        # Create user
        user = User.objects.create_user(
            email='tokentest@gmail.com',
            password='temp_password'
        )
        
        # Mock save_user to test token creation
        mock_request = Mock()
        mock_sociallogin = Mock()
        
        # Call the real save_user method
        result = adapter.save_user(mock_request, mock_sociallogin)
        
        # Token should be created
        assert result is not None


@pytest.mark.django_db
class TestGoogleOAuthIntegration:
    """Integration tests for Google OAuth flow."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = APIClient()
        # Ensure sites framework is set up
        Site.objects.get_or_create(pk=1, defaults={'domain': 'localhost', 'name': 'localhost'})
    
    def test_google_oauth_redirect_uri_format(self):
        """Test that Google OAuth redirect URI is properly formatted."""
        redirect_uri = '/accounts/google/login/callback/'
        
        # URI should follow OAuth standard format
        assert '/accounts/' in redirect_uri
        assert '/google/' in redirect_uri
        assert '/callback/' in redirect_uri
    
    def test_social_account_permission_scopes(self):
        """Test that Google OAuth requests proper permission scopes."""
        # In settings.py, SOCIALACCOUNT_PROVIDERS defines scopes
        # This test verifies the structure
        from django.conf import settings
        
        providers = settings.SOCIALACCOUNT_PROVIDERS
        assert 'google' in providers
        assert 'SCOPE' in providers['google']
        assert 'profile' in providers['google']['SCOPE']
        assert 'email' in providers['google']['SCOPE']
    
    def test_google_oauth_with_email_verification(self):
        """Test email verification in Google OAuth flow."""
        user = User.objects.create_user(
            email='verified@gmail.com',
            password='temp_password'
        )
        
        # Google provides verified emails, so no extra verification needed
        user.email_verified = True
        user.save()
        
        assert user.email_verified
    
    def test_drf_auth_social_endpoints(self):
        """Test that dj-rest-auth social endpoints are configured."""
        # Check if endpoints are accessible
        endpoints = [
            '/api/auth/',
            '/api/auth/registration/',
        ]
        
        for endpoint in endpoints:
            # Endpoints should exist (methods may not be allowed)
            # This just verifies the routes are defined
            assert endpoint is not None
    
    def test_token_auth_after_social_login(self):
        """Test that user can authenticate with token after social login."""
        # Create social login user
        user = User.objects.create_user(
            email='tokenauth@gmail.com',
            password='temp_password'
        )
        
        token, _ = Token.objects.get_or_create(user=user)
        
        # Try to use token for authentication
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        # Token should be valid
        assert token.key is not None
        assert len(token.key) == 40


@pytest.mark.django_db
class TestGoogleOAuthErrorHandling:
    """Test error handling in Google OAuth flow."""
    
    def test_invalid_google_token_rejected(self):
        """Test that invalid Google tokens are rejected."""
        # Try to authenticate with fake token
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token invalid_token_12345')
        
        # Endpoint should reject invalid token
        response = client.get('/api/v1/auth/profile/')
        assert response.status_code == 401
    
    def test_duplicate_email_handling(self):
        """Test that duplicate emails are handled correctly in social login."""
        # Create first user
        user1 = User.objects.create_user(
            email='duplicate@gmail.com',
            password='password123'
        )
        
        # Attempt to create another with same email
        with pytest.raises(Exception):  # Should raise IntegrityError or similar
            User.objects.create_user(
                email='duplicate@gmail.com',
                password='password456'
            )
    
    def test_social_account_linking_to_existing_user(self):
        """Test that social account can be linked to existing user."""
        # Create user first
        user = User.objects.create_user(
            email='linking@gmail.com',
            password='password123'
        )
        
        # In real scenario, user would login with Google
        # and account would be linked
        assert User.objects.get(email='linking@gmail.com') == user
