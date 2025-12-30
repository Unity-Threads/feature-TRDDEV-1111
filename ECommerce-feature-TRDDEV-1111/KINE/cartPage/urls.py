# Import the path function to define URL routes
from django.urls import path

# Import all the view functions from views.py
from . import views
urlpatterns = [
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cartPage'),
    path("update-cart/<int:item_id>/", views.update_cart, name="update_cart"),
]