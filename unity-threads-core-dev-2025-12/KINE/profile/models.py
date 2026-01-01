from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, default='avatars/default-avatar.png')

    phone_number = models.CharField(max_length=15, default='9999999999')

    def __str__(self):
        return self.user.username
