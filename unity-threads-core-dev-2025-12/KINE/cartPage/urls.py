from django.urls import path
from . import views

app_name = 'cartPage'

urlpatterns = [
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('', views.cart, name='cartPage'),
    path('update-cart/<int:item_id>/', views.update_cart, name='update_cart'),
    path('check/', views.check_cart_item, name='check_cart_item'),
]
