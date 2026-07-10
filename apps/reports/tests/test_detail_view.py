import pytest
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from rest_framework.test import APIClient

from apps.reports.models import Report, Category
from apps.users.tests.conftest import make_test_password

User = get_user_model()

TEST_PASSWORD = make_test_password()

# =========================
# CLIENT
# =========================


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def authenticated_client(client, user):
    """
    Cliente ya autenticado para evitar repetir force_authenticate en tests
    """
    client.force_authenticate(user=user)
    return client


# =========================
# USERS
# =========================


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="user", password=TEST_PASSWORD, role="CITIZEN"
    )


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        username="admin", password=TEST_PASSWORD, role="ADMIN"
    )


@pytest.fixture
def citizen_user(db):
    return User.objects.create_user(
        username="citizen", password=TEST_PASSWORD, role="CITIZEN"
    )


# =========================
# CATEGORY
# =========================


@pytest.fixture
def category(db):
    return Category.objects.create(name="General")


# =========================
# REPORT FACTORY
# =========================


@pytest.fixture
def report_factory(db, user, category):

    def create_report(**kwargs):

        owner = kwargs.get("created_by") or kwargs.get("user") or user

        # evitar strings accidentales
        if isinstance(owner, str):
            raise ValueError("created_by debe ser un objeto User, no un string")

        return Report.objects.create(
            title=kwargs.get("title", "Test report"),
            detail=kwargs.get("detail", "Some detail"),
            status=kwargs.get("status", "PENDING"),
            created_by=owner,
            category=kwargs.get("category", category),
            location=kwargs.get("location") or Point(0, 0, srid=4326),
        )

    return create_report


@pytest.fixture
def reports_factory(report_factory):

    def create_many(n=5, **kwargs):
        return [report_factory(**kwargs) for _ in range(n)]

    return create_many


def test_report_list_order(authenticated_client, reports_factory):
    response = authenticated_client.get("/api/reports/all/")

    statuses = [r["status"] for r in response.data["results"]]

    assert statuses == sorted(statuses)


def test_citizen_cannot_see_others_report(client, citizen_user, report_factory):
    other_user = citizen_user.__class__.objects.create_user(
        username="other", password=TEST_PASSWORD, role="CITIZEN"
    )

    other_report = report_factory(created_by=other_user)

    client.force_authenticate(user=citizen_user)

    response = client.get(f"/api/reports/{other_report.id}/")

    assert response.status_code == 404


def test_admin_can_see_any_report(client, admin_user, report_factory):
    report = report_factory()

    client.force_authenticate(user=admin_user)

    response = client.get(f"/api/reports/{report.id}/")

    assert response.status_code == 200


def test_soft_delete_report(client, user, report_factory):
    report = report_factory(created_by=user)

    client.force_authenticate(user=user)

    response = client.delete(f"/api/reports/{report.id}/")

    report.refresh_from_db()

    assert response.status_code == 204
    assert report.deleted_at is not None


def test_citizen_update_report(client, citizen_user, report_factory):
    report = report_factory(created_by=citizen_user)

    client.force_authenticate(user=citizen_user)

    response = client.patch(
        f"/api/reports/{report.id}/update/",
        {"title": "nuevo titulo"},
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.data["title"] == "nuevo titulo"


def test_citizen_cannot_update_status(client, citizen_user, report_factory):
    report = report_factory(created_by=citizen_user)

    client.force_authenticate(user=citizen_user)

    response = client.patch(
        f"/api/reports/{report.id}/update/",
        {"status": "RESOLVED"},
        content_type="application/json",
    )

    assert response.status_code == 400


def test_citizen_cannot_update_other_report(client, citizen_user, report_factory):
    report = report_factory()

    client.force_authenticate(user=citizen_user)

    response = client.patch(
        f"/api/reports/{report.id}/update/",
        {"title": "hack"},
        content_type="application/json",
    )

    assert response.status_code == 404


def test_admin_update_status(client, admin_user, report_factory):
    report = report_factory()

    client.force_authenticate(user=admin_user)

    response = client.patch(
        f"/api/reports/{report.id}/status/",
        {"status": "RESOLVED", "update_detail": "report detail"},
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.data["status"] == "RESOLVED"


def test_admin_cannot_use_citizen_endpoint(client, admin_user, report_factory):
    report = report_factory(created_by=admin_user)

    client.force_authenticate(user=admin_user)

    response = client.patch(
        f"/api/reports/{report.id}/update/",
        {"title": "fail"},
        content_type="application/json",
    )

    assert response.status_code == 403


def test_citizen_cannot_use_admin_endpoint(client, citizen_user, report_factory):
    report = report_factory(created_by=citizen_user)

    client.force_authenticate(user=citizen_user)

    response = client.patch(
        f"/api/reports/{report.id}/status/",
        {"status": "RESOLVED"},
        content_type="application/json",
    )

    assert response.status_code == 403


def test_report_not_found(client, admin_user):
    client.force_authenticate(user=admin_user)

    response = client.patch(
        "/api/reports/999/status/",
        {"status": "RESOLVED"},
        content_type="application/json",
    )

    assert response.status_code == 404


def test_report_list_my_reports_filter(client, citizen_user, report_factory):
    # Create a report by this citizen
    my_report = report_factory(created_by=citizen_user, title="My citizen report")

    # Create another report by another user
    other_user = citizen_user.__class__.objects.create_user(
        username="other_citizen", password=TEST_PASSWORD, role="CITIZEN"
    )
    other_report = report_factory(created_by=other_user, title="Other report")

    client.force_authenticate(user=citizen_user)

    # Get all reports
    response_all = client.get("/api/reports/all/")
    assert response_all.status_code == 200
    results_all = [r["id"] for r in response_all.data["results"]]
    assert my_report.id in results_all
    assert other_report.id in results_all

    # Get only my reports
    response_my = client.get("/api/reports/all/?my_reports=true")
    assert response_my.status_code == 200
    results_my = [r["id"] for r in response_my.data["results"]]
    assert my_report.id in results_my
    assert other_report.id not in results_my

