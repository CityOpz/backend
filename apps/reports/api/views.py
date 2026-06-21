# Create Report view

from rest_framework import generics, permissions
from apps.reports.models import Report
from apps.reports.api.serializers import ReportSerializer, ReportStatusUpdateSerializer
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser


class ReportCreateView(generics.CreateAPIView):
    queryset = Report.objects.all().filter(deleted_at__isnull=True)
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
