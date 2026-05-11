"""
Profile tests for the authentication module.
Adds coverage for fetching and updating the authenticated user's profile.
"""
import pytest
from rest_framework import status


@pytest.mark.django_db
class TestProfileView:
    def test_get_profile_returns_authenticated_user(self, authenticated_api_client):
        api_client, user, _ = authenticated_api_client

        response = api_client.get('/api/v1/auth/profile/')

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['phone_number'] == user.phone_number
        assert data['email'] == user.email

    def test_update_profile_persists_changes(self, authenticated_api_client):
        api_client, user, _ = authenticated_api_client

        response = api_client.put(
            '/api/v1/auth/profile/',
            {
                'first_name': 'Ali',
                'last_name': 'Khan',
            },
            format='json',
        )

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.first_name == 'Ali'
        assert user.last_name == 'Khan'
        assert response.json()['first_name'] == 'Ali'
        assert response.json()['last_name'] == 'Khan'
