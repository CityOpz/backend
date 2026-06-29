from contextlib import nullcontext

from django.conf import settings
from django.db import models
from django.db.models.fields import related
from django.contrib.gis.db import models as geomodels

# Create your models here.


class Report(models.Model):
    """
    Model representing a report of an issue in the city.
    """

    class Status(models.TextChoices):
        PENDING = "PENDING"
        IN_REVIEW = "IN_REVIEW"
        IN_REPAIR = "IN_REPAIR"
        RESOLVED = "RESOLVED"

    category = models.ForeignKey(
        "reports.Category", on_delete=models.PROTECT, related_name="reports"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="reports"
    )

    title = models.CharField(max_length=60, null=False, blank=False)
    detail = models.TextField(help_text="Details on the report")
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True
    )
    photo = models.ImageField(upload_to="report_photos/", null=True, blank=True)

    # Location is a geometry(Point, 4326) field from postgis
    location = geomodels.PointField(srid=4326, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.title} - {self.status}"


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True, null=False, blank=False)
    description = models.TextField(
        help_text="Description of the category", null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ReportStatusHistory(models.Model):
    """
    Model to keep track of the status update of the report
    """

    class Status(models.TextChoices):
        PENDING = "PENDING"
        IN_REVIEW = "IN_REVIEW"
        IN_REPAIR = "IN_REPAIR"
        RESOLVED = "RESOLVED"

    report = models.ForeignKey(
        "reports.Report", on_delete=models.CASCADE, related_name="status_history"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="status_updates",
    )
    new_status = models.CharField(max_length=20, choices=Status.choices)
    previous_status = models.CharField(max_length=20, choices=Status.choices)
    update_detail = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
