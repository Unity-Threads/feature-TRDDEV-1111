from django.urls import path
from . import views


urlpatterns = [
    path('season_shop/', views.shop, name='season_shop'),
    path("category-shop/", views.category_shop, name="category_shop"),
    path("product-type-shop/", views.producttype_shop, name="product_type_shop"),
    path("accessories-shop/", views.accessories_shop, name="accessories_shop"),
    path('products/', views.product_list, name='product_list'),
    path("products/<int:pk>/", views.product_detail, name="product_detail"),
]
