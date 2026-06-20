from .views import ReportCreateView
from django.urls import path


urlpatterns = [
    path("", ReportCreateView.as_view(), name="report-create"),
]
