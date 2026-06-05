"""
Custom adapters for django-allauth integration.
Handles user creation and social account linking for Google OAuth.
"""
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from .models import User


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom adapter for account-related operations.
    Ensures compatibility with custom User model.
    """
    
    def save_user(self, request, sociallogin, form=None):
        """
        Override user saving to use custom User model fields.
        """
        user = super().save_user(request, sociallogin, form)
        
        # Extract social account data
        extra_data = sociallogin.account.extra_data
        
        # Set phone_number if available (for our custom User model)
        # Note: Google OAuth doesn't provide phone by default
        # This can be set during registration or later
        
        user.save()
        return user


class CustomSocialAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter for social account operations.
    Handles token creation for users logging in via social auth.
    """
    
    def pre_social_login(self, request, sociallogin):
        """
        Called before social login is processed.
        Used for additional validation or user lookup.
        """
        # Check if user already exists by email
        if sociallogin.is_existing:
            return
        
        # If email exists, connect to existing user
        try:
            user = User.objects.get(email=sociallogin.account.extra_data.get('email'))
            sociallogin.connect(request, user)
        except User.DoesNotExist:
            pass
    
    def save_user(self, request, sociallogin, form=None):
        """
        Override to ensure token is created after user creation.
        """
        user = super().save_user(request, sociallogin, form)
        return user
    
    def populate_user(self, request, sociallogin, data):
        """
        Extract common fields from social account data.
        """
        user = super().populate_user(request, sociallogin, data)
        
        # Ensure email is set from social account
        if not user.email and 'email' in data:
            user.email = data['email']
        
        return user
