"""
Custom authentication classes for token validation.
"""
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone


class CustomTokenAuthentication(TokenAuthentication):
    """Custom token authentication that validates token expiry."""
    
    def authenticate(self, request):
        """Authenticate token and check expiry."""
        result = super().authenticate(request)
        
        if result is None:
            return None
        
        user, token = result
        
        # Check if token has expired field and validate
        if hasattr(token, 'expires_at') and token.expires_at and token.expires_at < timezone.now():
            raise AuthenticationFailed('Token has expired.')
        
        return user, token
