from django.urls import path
from . import views

urlpatterns = [
    path('', views.wishlist_view, name='wishlist_view'),
    path('toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
]