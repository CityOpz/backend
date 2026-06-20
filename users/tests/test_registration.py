import pytest

from users.models import User


@pytest.mark.django_db
def test_register_user_success(client):

    data = {
        "username": "usuario_test",
        "email": "test@test.com",
        "first_name": "Juan",
        "last_name": "Perez",
        "password": "12345678",
    }

    response = client.post(
        "/api/users/register/", data, content_type="application/json"
    )

    assert response.status_code == 201

    user = User.objects.get(username="usuario_test")

    assert user.email == "test@test.com"
    assert user.role == "CITIZEN"


@pytest.mark.django_db
def test_register_duplicate_user(client):

    User.objects.create_user(
        username="juan",
        first_name="Usuario",
        last_name="Perez",
        email="juan@test.com",
        password="12345678",
    )

    response = client.post(
        "/api/users/register/",
        {
            "username": "juan",
            "first_name": "Usuario",
            "last_name": "Perez",
            "email": "juan2@test.com",
            "password": "12345678",
        },
        content_type="application/json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_register_duplicate_email(client):

    User.objects.create_user(
        username="juan",
        first_name="Usuario",
        last_name="Perez",
        email="correo@gmail.com",
        password="12345678",
    )

    response = client.post(
        "/api/users/register/",
        {
            "username": "pedro",
            "first_name": "Usuario",
            "last_name": "Perez",
            "email": "correo@gmail.com",
            "password": "12345678",
        },
        content_type="application/json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_register_cannot_create_admin(client):

    response = client.post(
        "/api/users/register/",
        {
            "username": "hacker",
            "email": "hack@gmail.com",
            "first_name": "Usuario",
            "last_name": "Perez",
            "password": "12345678",
            "role": "ADMIN",
        },
        content_type="application/json",
    )

    assert response.status_code == 201

    user = User.objects.get(username="hacker")

    assert user.role == "CITIZEN"


@pytest.mark.django_db
def test_register_without_password(client):

    response = client.post(
        "/api/users/register/",
        {
            "first_name": "Usuario",
            "last_name": "Perez",
            "username": "juan",
            "email": "juan@gmail.com",
        },
        content_type="application/json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_user_created_in_database(client):

    client.post(
        "/api/users/register/",
        {
            "username": "maria",
            "first_name": "Usuario",
            "last_name": "Perez",
            "email": "maria@gmail.com",
            "password": "12345678",
        },
        content_type="application/json",
    )

    assert User.objects.filter(username="maria").exists()

