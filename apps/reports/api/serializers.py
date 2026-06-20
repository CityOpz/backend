from rest_framework import serializers
from apps.users.models import User
from apps.reports.models import Category, Report
from django.contrib.gis.geos import Point


class ReportCreatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]
        read_only_fields = fields


class ReportCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description"]
        read_only_fields = fields


# Citizens can create reports, but they cannot upadate the status of the report.
# Only Administrators can update the status of the report.
class ReportSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(write_only=True)
    longitude = serializers.FloatField(write_only=True)

    category = ReportCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source="category", write_only=True
    )
    created_by = ReportCreatorSerializer(read_only=True)

    title = serializers.CharField(max_length=60, min_length=1)

    class Meta:
        model = Report
        fields = [
            "id",
            "category",
            "category_id",
            "title",
            "detail",
            "status",
            "photo",
            "latitude",
            "longitude",
            "created_at",
            "updated_at",
            "category",
            "created_by",
        ]
        read_only_fields = ["id", "status", "created_at", "updated_at", "created_by"]

    def create(self, validated_data):
        """
        Override the create method to handle the latitude and longitude fields and convert them into a Point object.
        """
        latitude = validated_data.pop("latitude")
        longitude = validated_data.pop("longitude")

        validated_data["location"] = Point(longitude, latitude, srid=4326)

        return super().create(validated_data)

    def to_representation(self, instance):
        """
        Override the to_representation method to include latitude and longitude in the response.
        """
        data = super().to_representation(instance)

        if instance.location:
            data["latitude"] = instance.location.y
            data["longitude"] = instance.location.x

        return data


class ReportStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating the status of a report. Only the status field is updatable.
    """

    class Meta:
        model = Report
        fields = ["status"]
