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

    path("shop_by_season/", views.shop_by_season, name="shop_by_season"),
    path("high_vibes/", views.high_vibes, name="high_vibes"),
    path("low_vibes/", views.low_vibes, name="low_vibes"),
    path("accessories/", views.accessories, name="accessories"),
    path("shop_now/", views.shop_now, name="shop_now"),
    path("logout/", views.logout_page, name="logout"),
    path("api/categories/", views.get_enabled_categories, name="get_categories"),
]
