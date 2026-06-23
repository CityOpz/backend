from .views import ReportCreateView, ReportListView, ReportDetailView
from django.urls import path


urlpatterns = [
    path("", ReportCreateView.as_view(), name="report-create"),
    path("all/", ReportListView.as_view(), name="report-list"),
    path("<int:pk>/", ReportDetailView.as_view(), name="report-detail"),
]
