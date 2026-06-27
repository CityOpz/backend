from .views import ReportCreateView, ReportListView, ReportDetailView, ReportUpdateView, ReportStatusUpdateView
from django.urls import path


urlpatterns = [
    path("", ReportCreateView.as_view(), name="report-create"),
    path("all/", ReportListView.as_view(), name="report-list"),
    path("<int:pk>/", ReportDetailView.as_view(), name="report-detail"),
    path("<int:pk>/update/",ReportUpdateView.as_view(),name="report-update"),
    path("<int:pk>/status/",ReportStatusUpdateView.as_view(),name="report-status-update"),
]
