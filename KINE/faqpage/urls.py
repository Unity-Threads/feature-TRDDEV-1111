from django.urls import path
from . import views

urlpatterns = [
    path("faqs/", views.faq_page, name="faqs"),

    # AJAX API endpoint
    path("faq/category/<int:cat_id>/", views.get_faqs_by_category, name="faq-category"),
]
