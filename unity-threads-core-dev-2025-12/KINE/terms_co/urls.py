from django.urls import path
from .views import terms_view

app_name = 'terms_co'   # ✅ THIS IS MANDATORY

urlpatterns = [
    path('terms_conditions/', terms_view, name='terms'),
]
