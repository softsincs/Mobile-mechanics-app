"""
URL Configuration for Authentication Module

Routes all authentication endpoints to their corresponding views.

API Endpoints:
- POST /api/v1/auth/signup/ - User registration
- POST /api/v1/auth/login/ - User login
- POST /api/v1/auth/send-otp/ - Request OTP
- POST /api/v1/auth/verify-otp/ - Verify OTP
- POST /api/v1/auth/forgot-password/ - Request password reset
- POST /api/v1/auth/reset-password/ - Reset password
- POST /api/v1/auth/change-password/ - Change password (authenticated)
- POST /api/v1/auth/refresh-token/ - Refresh token
- GET /api/v1/auth/profile/ - Get user profile (authenticated)
- PUT /api/v1/auth/profile/ - Update user profile (authenticated)
"""

from django.urls import path
from . import views

app_name = "auth"

urlpatterns = [
    # ==================== USER AUTHENTICATION ====================
    # Registration
    path("signup/", views.SignupView.as_view(), name="signup"),
    
    # Login (2-step: password + OTP)
    path("login/", views.LoginView.as_view(), name="login"),
    path("send-otp/", views.SendOTPView.as_view(), name="send-otp"),
    path("verify-otp/", views.VerifyOTPView.as_view(), name="verify-otp"),
    
    # Password Management
    path("forgot-password/", views.ForgotPasswordView.as_view(), name="forgot-password"),
    path("reset-password/", views.ResetPasswordView.as_view(), name="reset-password"),
    path("change-password/", views.ChangePasswordView.as_view(), name="change-password"),
    
    # Token Management
    path("refresh-token/", views.RefreshTokenView.as_view(), name="refresh-token"),
    
    # User Profile (Protected)
    path("profile/", views.ProfileView.as_view(), name="profile"),
]
