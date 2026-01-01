from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm
import re


class EmailChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            raise forms.ValidationError("Enter valid email")
        return email


class CustomPasswordChangeForm(DjangoPasswordChangeForm):
    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        if len(password) < 8 or \
           not re.search(r'[A-Z]', password) or \
           not re.search(r'[a-z]', password) or \
           not re.search(r'\d', password) or \
           not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
            raise forms.ValidationError(
                "Password must be 8+ chars with uppercase, lowercase, number & special character"
            )
        return password
