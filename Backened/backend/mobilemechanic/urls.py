"""
URL configuration for mobilemechanic project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication API
    path('api/v1/auth/', include('users.urls')),
    
    # Allauth URLs (for social authentication)
    path('accounts/', include('allauth.urls')),
    
    # DRF-Auth URLs (standard auth endpoints)
    path('api/auth/', include('dj_rest_auth.urls')),
    
    # DRF-Auth registration URLs (registration and social auth)
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
    # Services API
    path('api/v1/', include('services.urls')),
    
    # Bookings API
    path('api/v1/', include('bookings.urls')),
    
    # Payments API
    path('api/v1/', include('payments.urls')),
    
    # Dispatch API
    path('api/v1/', include('dispatch.urls')),
    
    # Tracking API
    path('api/v1/', include('tracking.urls')),

    # Ratings API
    path('api/v1/', include('ratings.urls')),

    # Notifications API
    path('api/v1/', include('notifications.urls')),

    # Mechanics API
    path('api/v1/', include('mechanics.urls')),

    # Analytics API
    path('api/v1/', include('analytics.urls')),
]
