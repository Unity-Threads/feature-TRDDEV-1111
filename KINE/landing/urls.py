from django.urls import path
from . import views

urlpatterns = [
    # -------------------------------
    # Home / Landing
    # -------------------------------
    path("", views.home, name="home"),
    path("landing/", views.landing, name="landing"),

    # -------------------------------
    # Pages
    # -------------------------------

    path("logout/", views.logout_page, name="logout1"),
    path("api/categories/", views.get_enabled_categories, name="get_categories"),
]
