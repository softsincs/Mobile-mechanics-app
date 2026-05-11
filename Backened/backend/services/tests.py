"""Pytest coverage for the `services` app."""

from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from .models import (
    MechanicServiceSpecialty,
    Service,
    ServiceAvailability,
    ServiceCategory,
    ServicePrice,
    ServicePromotion,
)
from .services import calculate_service_price


User = get_user_model()


@pytest.fixture
def service_user(db):
    return User.objects.create_user(
        phone_number='+923001234567',
        email='mechanic@example.com',
        password='SecurePass123!',
    )


@pytest.fixture
def auth_client(service_user):
    client = APIClient()
    token = Token.objects.create(user=service_user)
    client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    return client


@pytest.fixture
def service_category(db):
    return ServiceCategory.objects.create(
        name='Maintenance',
        description='Routine maintenance services',
        is_active=True,
    )


@pytest.fixture
def service_item(service_category):
    return Service.objects.create(
        category=service_category,
        name='Oil Change',
        description='Change engine oil',
        estimated_duration=30,
        base_price=Decimal('1200.00'),
        min_price=Decimal('1000.00'),
        max_price=Decimal('1500.00'),
        is_active=True,
    )


@pytest.fixture
def service_price(service_item):
    return ServicePrice.objects.create(
        service=service_item,
        city='Lahore',
        peak_multiplier=Decimal('1.50'),
        off_peak_multiplier=Decimal('1.00'),
        weekend_multiplier=Decimal('1.25'),
        valid_from=timezone.now() - timedelta(days=1),
    )


@pytest.fixture
def service_availability(service_item):
    return ServiceAvailability.objects.create(
        service=service_item,
        city='Lahore',
        is_available=True,
        notes='Available all week',
    )


@pytest.fixture
def promotion(service_item):
    return ServicePromotion.objects.create(
        code='SAVE10',
        title='Save 10%',
        description='10 percent off maintenance services',
        service=service_item,
        city='Lahore',
        discount_type='PERCENTAGE',
        discount_value=Decimal('10.00'),
        max_discount_amount=Decimal('500.00'),
        min_booking_amount=Decimal('500.00'),
        valid_from=timezone.now() - timedelta(days=1),
        valid_to=timezone.now() + timedelta(days=7),
        is_active=True,
    )


@pytest.fixture
def mechanic_with_specialty(service_user, service_item):
    MechanicServiceSpecialty.objects.create(
        mechanic=service_user,
        service=service_item,
        proficiency_level='EXPERT',
        years_experience=5,
        is_active=True,
    )
    return service_user


@pytest.fixture
def service_with_related_data(service_item, service_availability, promotion):
    return service_item


@pytest.fixture
def booking_datetime():
    return timezone.make_aware(datetime(2026, 5, 8, 18, 0, 0))


def results(data):
    return data['results'] if isinstance(data, dict) and 'results' in data else data


@pytest.mark.django_db
class TestServiceModels:
    def test_service_category_str(self, service_category):
        assert str(service_category) == 'Maintenance'

    def test_service_str(self, service_item):
        assert str(service_item) == 'Oil Change'

    def test_service_price_str(self, service_price):
        assert str(service_price) == 'Oil Change - Lahore'

    def test_service_availability_str(self, service_availability):
        assert str(service_availability) == 'Oil Change in Lahore'

    def test_specialty_str(self, mechanic_with_specialty, service_item):
        specialty = MechanicServiceSpecialty.objects.get(mechanic=mechanic_with_specialty, service=service_item)
        assert 'EXPERT' in str(specialty)

    def test_promotion_discount_calculation(self, promotion):
        assert promotion.calculate_discount(Decimal('1000.00')) == Decimal('100.00')


@pytest.mark.django_db
class TestServicePermissions:
    def test_unauthenticated_service_list_is_denied(self):
        client = APIClient()
        response = client.get(reverse('service-list'))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authenticated_service_list_returns_data(self, auth_client, service_item, service_availability, promotion):
        response = auth_client.get(reverse('service-list'))

        assert response.status_code == status.HTTP_200_OK
        data = results(response.data)
        assert len(data) == 1
        assert data[0]['name'] == service_item.name
        assert data[0]['category']['name'] == service_item.category.name
        assert data[0]['availability_slots'][0]['city'] == 'Lahore'
        assert data[0]['promotions'][0]['code'] == 'SAVE10'


@pytest.mark.django_db
class TestServiceCatalogApi:
    def test_filter_services_by_category(self, auth_client, service_item):
        response = auth_client.get(reverse('service-list'), {'category': 'Maintenance'})

        assert response.status_code == status.HTTP_200_OK
        data = results(response.data)
        assert len(data) == 1
        assert data[0]['name'] == service_item.name

    def test_filter_services_by_city(self, auth_client, service_item, service_availability):
        response = auth_client.get(reverse('service-list'), {'city': 'Lahore'})

        assert response.status_code == status.HTTP_200_OK
        data = results(response.data)
        assert len(data) == 1
        assert data[0]['name'] == service_item.name

    def test_create_category_and_service(self, auth_client):
        category_response = auth_client.post(
            reverse('servicecategory-list'),
            {
                'name': 'Repair',
                'description': 'Repair services',
                'icon_url': 'https://example.com/icon.png',
                'is_active': True,
            },
            format='json',
        )

        assert category_response.status_code == status.HTTP_201_CREATED

        service_response = auth_client.post(
            reverse('service-list'),
            {
                'category_id': category_response.data['id'],
                'name': 'Battery Replacement',
                'description': 'Replace battery',
                'estimated_duration': 45,
                'base_price': '2500.00',
                'min_price': '2200.00',
                'max_price': '3000.00',
                'is_active': True,
            },
            format='json',
        )

        assert service_response.status_code == status.HTTP_201_CREATED
        assert service_response.data['name'] == 'Battery Replacement'
        assert service_response.data['category']['name'] == 'Repair'

    def test_reject_invalid_category_id(self, auth_client):
        response = auth_client.post(
            reverse('service-list'),
            {
                'category_id': '00000000-0000-0000-0000-000000000000',
                'name': 'Battery Replacement',
                'description': 'Replace battery',
                'estimated_duration': 45,
                'base_price': '2500.00',
                'is_active': True,
            },
            format='json',
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'category_id' in response.data


@pytest.mark.django_db
class TestServicePricingApi:
    def test_pricing_action_returns_dynamic_breakdown(self, auth_client, service_item, service_price, promotion, mechanic_with_specialty, booking_datetime):
        response = auth_client.get(
            reverse('service-pricing', args=[service_item.id]),
            {
                'city': 'Lahore',
                'booking_datetime': booking_datetime.isoformat(),
                'promo_code': 'SAVE10',
                'mechanic_id': str(mechanic_with_specialty.id),
            },
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['city'] == 'Lahore'
        assert response.data['pricing_profile']['service'] == service_item.id
        calculation = response.data['calculation']
        assert calculation['promotion_code'] == 'SAVE10'
        assert calculation['mechanic_multiplier'] == '1.15' or str(calculation['mechanic_multiplier']) == '1.15'
        assert Decimal(str(calculation['discount_amount'])) > Decimal('0')
        assert Decimal(str(calculation['total_amount'])) > Decimal('0')

    def test_service_price_lookup_profile_endpoint_still_works(self, auth_client, service_item, service_price):
        response = auth_client.get(
            reverse('service-pricing', args=[service_item.id]),
            {'city': 'Lahore'},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['pricing_profile']['city'] == 'Lahore'

    def test_service_category_price_availability_and_promotion_lists_are_accessible(self, auth_client, service_category, service_price, service_availability, promotion):
        category_response = auth_client.get(reverse('servicecategory-list'))
        price_response = auth_client.get(reverse('serviceprice-list'))
        availability_response = auth_client.get(reverse('serviceavailability-list'))
        promotion_response = auth_client.get(reverse('servicepromotion-list'))

        assert category_response.status_code == status.HTTP_200_OK
        assert price_response.status_code == status.HTTP_200_OK
        assert availability_response.status_code == status.HTTP_200_OK
        assert promotion_response.status_code == status.HTTP_200_OK
        assert len(results(category_response.data)) == 1
        assert len(results(price_response.data)) == 1
        assert len(results(availability_response.data)) == 1
        assert len(results(promotion_response.data)) == 1

    def test_mechanic_specialty_list_and_filter(self, auth_client, mechanic_with_specialty, service_item):
        response = auth_client.get(reverse('mechanicservicespecialty-list'))
        filtered = auth_client.get(reverse('mechanicservicespecialty-list'), {'mechanic_id': str(mechanic_with_specialty.id)})

        assert response.status_code == status.HTTP_200_OK
        assert filtered.status_code == status.HTTP_200_OK
        assert len(results(response.data)) == 1
        assert len(results(filtered.data)) == 1
        assert results(filtered.data)[0]['service'] == service_item.id

    def test_service_list_includes_nested_related_data(self, auth_client, service_item, service_availability, promotion):
        response = auth_client.get(reverse('service-list'))

        assert response.status_code == status.HTTP_200_OK
        data = results(response.data)
        assert data[0]['prices'] == []
        assert data[0]['availability_slots'][0]['city'] == 'Lahore'
        assert data[0]['promotions'][0]['code'] == 'SAVE10'

    def test_calculate_service_price_helper_matches_api_shape(self, service_item, service_price, promotion, mechanic_with_specialty, booking_datetime):
        calculation = calculate_service_price(
            service=service_item,
            city='Lahore',
            booking_datetime=booking_datetime,
            mechanic=mechanic_with_specialty,
            promo_code='SAVE10',
        )

        assert calculation['promotion_code'] == 'SAVE10'
        assert calculation['pricing_profile']['id'] == service_price.id
        assert Decimal(str(calculation['subtotal'])) > Decimal('0')
        assert Decimal(str(calculation['total_amount'])) > Decimal('0')
