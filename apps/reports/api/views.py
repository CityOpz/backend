# Create Report view

from rest_framework.pagination import PageNumberPagination
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from apps.reports.models import Report, ReportStatusHistory
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from apps.reports.api.serializers import (
    ReportSerializer,
    ReportStatusUpdateSerializer,
    ReportListSerializer,
    ReportCitizenUpdateSerializer,
)
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.utils import timezone
from django.db.models import Case, When, Value, IntegerField
from django.db import transaction


class ReportCreateView(generics.CreateAPIView):
    queryset = Report.objects.all().filter(deleted_at__isnull=True)
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ReportPagination(PageNumberPagination):
    page_size = 10


class ReportListView(generics.ListAPIView):
    serializer_class = ReportListSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ReportPagination

    def get_queryset(self):
        qs = Report.objects.filter(deleted_at__isnull=True)
        if self.request.query_params.get("my_reports") == "true":
            qs = qs.filter(created_by=self.request.user)
        return (
            qs.annotate(
                status_order=Case(
                    When(status="PENDING", then=Value(1)),
                    When(status="IN_REVIEW", then=Value(2)),
                    When(status="IN_REPAIR", then=Value(3)),
                    When(status="RESOLVED", then=Value(4)),
                    output_field=IntegerField(),
                )
            )
            .order_by("status_order", "-created_at")
        )


class ReportDetailView(generics.RetrieveDestroyAPIView):
    queryset = Report.objects.filter(deleted_at__isnull=True)
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def _get_user_role(self):
        user = getattr(self.request, "user", None)

        if not getattr(user, "is_authenticated", False):
            return None

        return getattr(user, "role", None)

    def get_queryset(self):
        qs = super().get_queryset()

        if self._get_user_role() == "CITIZEN":
            return qs.filter(created_by=self.request.user)

        return qs

    def destroy(self, request, *args, **kwargs):
        report = self.get_object()

        report.deleted_at = timezone.now()
        report.save(update_fields=["deleted_at"])

        return Response(status=status.HTTP_204_NO_CONTENT)


class ReportUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=ReportCitizenUpdateSerializer, responses=ReportCitizenUpdateSerializer
    )
    def patch(self, request, pk):

        if getattr(request.user, "role", None) != "CITIZEN":
            raise PermissionDenied(
                "Solo los ciudadanos pueden actualizar este reporte."
            )

        try:
            report = Report.objects.get(
                pk=pk, deleted_at__isnull=True, created_by=request.user
            )

        except Report.DoesNotExist:
            return Response(
                {"detail": "Reporte no encontrado."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = ReportCitizenUpdateSerializer(
            report, data=request.data, partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class ReportStatusUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=ReportStatusUpdateSerializer, responses=ReportSerializer)
    @transaction.atomic
    def patch(self, request, pk):
        if getattr(request.user, "role", None) != "ADMIN":
            raise PermissionDenied(
                "Solo los administradores pueden modificar el estado."
            )

        try:
            report = Report.objects.get(pk=pk, deleted_at__isnull=True)

        except Report.DoesNotExist:
            return Response(
                {"detail": "Reporte no encontrado."}, status=status.HTTP_404_NOT_FOUND
            )

        previous_status = report.status

        serializer = ReportStatusUpdateSerializer(
            report, data=request.data, partial=True
        )

        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data.get("status")
        update_detail = serializer.validated_data.get("update_detail")

        serializer.save()

        ReportStatusHistory.objects.create(
            report=report,
            updated_by=request.user,
            new_status=new_status,
            previous_status=previous_status,
            update_detail=update_detail,
        )

        return Response(ReportSerializer(report).data, status=status.HTTP_200_OK)

