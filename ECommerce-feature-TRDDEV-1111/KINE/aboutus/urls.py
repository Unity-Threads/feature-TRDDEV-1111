from django.urls import path
from . import views

urlpatterns = [
    path("about/", views.aboutus, name="about"),
]
