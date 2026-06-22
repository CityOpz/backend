import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from .conftest import make_test_password

pytestmark = pytest.mark.django_db


LOGIN_URL = "/api/token/"
TEST_PASSWORD = make_test_password()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_user():
    User = get_user_model()

    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": TEST_PASSWORD,
    }

    return User.objects.create_user(**user_data)


def test_login_success(api_client, test_user):
    payload = {
        "username": "testuser",
        "password": TEST_PASSWORD,
    }

    response = api_client.post(LOGIN_URL, payload, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert "refresh" in response.data


def test_login_fails_with_wrong_password(api_client, test_user):
    payload = {
        "username": "testuser",
        "password": make_test_password(),
    }

    response = api_client.post(LOGIN_URL, payload, format="json")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "access" not in response.data
    assert "refresh" not in response.data


def test_login_fails_with_nonexistent_user(api_client):
    payload = {
        "username": "nouser",
        "password": TEST_PASSWORD,
    }

    response = api_client.post(LOGIN_URL, payload, format="json")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "access" not in response.data
    assert "refresh" not in response.data


def test_login_fails_without_username(api_client):
    payload = {
        "password": TEST_PASSWORD,
    }

    response = api_client.post(LOGIN_URL, payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "access" not in response.data
    assert "refresh" not in response.data


def test_login_fails_without_password(api_client):
    payload = {
        "username": "testuser",
    }

    response = api_client.post(LOGIN_URL, payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "access" not in response.data
    assert "refresh" not in response.data
