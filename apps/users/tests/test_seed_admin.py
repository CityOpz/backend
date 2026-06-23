import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.utils.crypto import get_random_string


pytestmark = pytest.mark.django_db


def make_test_password():
    return f"Test-{get_random_string(16)}-A1!"


def test_seed_admin_does_not_create_user_when_env_vars_are_missing(monkeypatch):
    monkeypatch.delenv("DEFAULT_ADMIN_USERNAME", raising=False)
    monkeypatch.delenv("DEFAULT_ADMIN_EMAIL", raising=False)
    monkeypatch.delenv("DEFAULT_ADMIN_PASSWORD", raising=False)
    monkeypatch.delenv("DEFAULT_ADMIN_ROLE", raising=False)

    call_command("seed_admin")

    user_model = get_user_model()

    assert user_model.objects.count() == 0


def test_seed_admin_creates_admin_user_from_env_vars(monkeypatch):
    password = make_test_password()

    monkeypatch.setenv("DEFAULT_ADMIN_USERNAME", "admin_test")
    monkeypatch.setenv("DEFAULT_ADMIN_EMAIL", "admin@test.com")
    monkeypatch.setenv("DEFAULT_ADMIN_PASSWORD", password)
    monkeypatch.setenv("DEFAULT_ADMIN_ROLE", "ADMIN")

    call_command("seed_admin")

    user_model = get_user_model()
    user = user_model.objects.get(username="admin_test")

    assert user.email == "admin@test.com"
    assert user.role == "ADMIN"
    assert user.is_active is True
    assert user.check_password(password)


def test_seed_admin_does_not_duplicate_existing_admin(monkeypatch):
    password = make_test_password()

    monkeypatch.setenv("DEFAULT_ADMIN_USERNAME", "admin_test")
    monkeypatch.setenv("DEFAULT_ADMIN_EMAIL", "admin@test.com")
    monkeypatch.setenv("DEFAULT_ADMIN_PASSWORD", password)
    monkeypatch.setenv("DEFAULT_ADMIN_ROLE", "ADMIN")

    call_command("seed_admin")
    call_command("seed_admin")

    user_model = get_user_model()

    assert user_model.objects.filter(username="admin_test").count() == 1
