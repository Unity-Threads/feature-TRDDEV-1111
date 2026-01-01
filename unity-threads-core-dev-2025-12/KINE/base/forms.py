from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re

class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()
    mobile = forms.CharField(max_length=15)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already exists")
        return email

    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        # You can add regex to validate mobile number format
        if len(mobile) < 10:
            raise ValidationError("Enter valid mobile number")
        return mobile

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8 or not re.search(r'\d', password) or not re.search(r'[!@#$%^&*]', password):
            raise ValidationError("Password must be at least 8 chars, include number & special char")
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")
        if password != confirm:
            raise ValidationError("Passwords do not match")
