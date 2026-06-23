import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from apps.reports.models import Category, Report
from apps.users.tests.conftest import make_test_password


pytestmark = pytest.mark.django_db


REPORT_CREATE_URL = "/api/reports/"


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    User = get_user_model()

    return User.objects.create_user(
        username="citizen_user",
        email="citizen@example.com",
        password=make_test_password(),
        first_name="Citizen",
        last_name="User",
    )


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def category():
    category, _ = Category.objects.get_or_create(
        name="Public Lighting",
        description="Broken streetlights, damaged light poles, dark areas, or failures in public lighting infrastructure.",
    )
    return category


def test_create_report_success(authenticated_client, user, category):
    payload = {
        "category_id": category.id,
        "title": "Broken street light",
        "detail": "The street light near the park is not working.",
        "latitude": 3.4516,
        "longitude": -76.5320,
    }

    response = authenticated_client.post(REPORT_CREATE_URL, payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED

    assert Report.objects.count() == 1

    report = Report.objects.first()

    assert report is not None
    assert report.title == payload["title"]
    assert report.detail == payload["detail"]
    assert report.category == category
    assert report.created_by == user
    assert report.status == Report.Status.PENDING

    assert report.location.y == payload["latitude"]
    assert report.location.x == payload["longitude"]

    assert response.data["title"] == payload["title"]
    assert response.data["detail"] == payload["detail"]
    assert response.data["status"] == Report.Status.PENDING

    assert response.data["category"]["id"] == category.id
    assert response.data["category"]["name"] == category.name

    assert response.data["created_by"]["id"] == user.id

    assert response.data["latitude"] == payload["latitude"]
    assert response.data["longitude"] == payload["longitude"]


def test_create_report_requires_authentication(api_client, category):
    payload = {
        "category_id": category.id,
        "title": "Broken street light",
        "detail": "The street light near the park is not working.",
        "latitude": 3.4516,
        "longitude": -76.5320,
    }

    response = api_client.post(REPORT_CREATE_URL, payload, format="json")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert Report.objects.count() == 0


def test_create_report_requires_category(authenticated_client):
    payload = {
        "title": "Broken street light",
        "detail": "The street light near the park is not working.",
        "latitude": 3.4516,
        "longitude": -76.5320,
    }

    response = authenticated_client.post(REPORT_CREATE_URL, payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "category_id" in response.data
    assert Report.objects.count() == 0


def test_create_report_rejects_invalid_category(authenticated_client):
    payload = {
        "category_id": 999999,
        "title": "Broken street light",
        "detail": "The street light near the park is not working.",
        "latitude": 3.4516,
        "longitude": -76.5320,
    }

    response = authenticated_client.post(REPORT_CREATE_URL, payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "category_id" in response.data
    assert Report.objects.count() == 0


def test_create_report_requires_title(authenticated_client, category):
    payload = {
        "category_id": category.id,
        "detail": "The street light near the park is not working.",
        "latitude": 3.4516,
        "longitude": -76.5320,
    }

    response = authenticated_client.post(REPORT_CREATE_URL, payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "title" in response.data
    assert Report.objects.count() == 0


def test_create_report_requires_detail(authenticated_client, category):
    payload = {
        "category_id": category.id,
        "title": "Broken street light",
        "latitude": 3.4516,
        "longitude": -76.5320,
    }

    response = authenticated_client.post(REPORT_CREATE_URL, payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "detail" in response.data
    assert Report.objects.count() == 0


def test_create_report_requires_latitude(authenticated_client, category):
    payload = {
        "category_id": category.id,
        "title": "Broken street light",
        "detail": "The street light near the park is not working.",
        "longitude": -76.5320,
    }

    response = authenticated_client.post(REPORT_CREATE_URL, payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "latitude" in response.data
    assert Report.objects.count() == 0


def test_create_report_requires_longitude(authenticated_client, category):
    payload = {
        "category_id": category.id,
        "title": "Broken street light",
        "detail": "The street light near the park is not working.",
        "latitude": 3.4516,
    }

    response = authenticated_client.post(REPORT_CREATE_URL, payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "longitude" in response.data
    assert Report.objects.count() == 0


def test_create_report_rejects_invalid_latitude(authenticated_client, category):
    payload = {
        "category_id": category.id,
        "title": "Broken street light",
        "detail": "The street light near the park is not working.",
        "latitude": "invalid-latitude",
        "longitude": -76.5320,
    }

    response = authenticated_client.post(REPORT_CREATE_URL, payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "latitude" in response.data
    assert Report.objects.count() == 0


def test_create_report_rejects_invalid_longitude(authenticated_client, category):
    payload = {
        "category_id": category.id,
        "title": "Broken street light",
        "detail": "The street light near the park is not working.",
        "latitude": 3.4516,
        "longitude": "invalid-longitude",
    }

    response = authenticated_client.post(REPORT_CREATE_URL, payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "longitude" in response.data
    assert Report.objects.count() == 0
