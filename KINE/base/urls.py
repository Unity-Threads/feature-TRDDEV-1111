from django.urls import path
from . import views

app_name = "base"

urlpatterns = [
    # Signup + Landing
    path("signup", views.signup, name="signup"),
    path("login/", views.login_view, name="login"),  # login with password
    path("forgot-password/", views.forgot_password, name="forgot_password"),  # enter email/mobile for OTP
    path("forgot-password/reset/", views.forgot_password_reset, name="forgot_password_reset"),  # reset form
    path("login/options/", views.login_options, name="login_options"),  # choose login method
    # path("landing/", views.landing, name="landing"),  # after login
]

