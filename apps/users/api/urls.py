from django.urls import path
from .views import RegisterView, CustomTokenObtainPairView


urlpatterns = [path("register/", RegisterView.as_view()),
               path("token/", CustomTokenObtainPairView.as_view()),]
