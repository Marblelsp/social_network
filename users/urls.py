from django.urls import path
from django.contrib.auth import views
from . import views

urlpatterns = [
    path("signup/", views.SignUp.as_view(), name="signup"),
    
]
