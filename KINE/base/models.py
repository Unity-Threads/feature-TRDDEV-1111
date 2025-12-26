from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from datetime import datetime, timedelta

class TempOTP(models.Model):
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15, unique=True)
    email_otp = models.CharField(max_length=6)
    mobile_otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)

    def is_expired(self):
        return datetime.now() > self.created_at + timedelta(minutes=10)
