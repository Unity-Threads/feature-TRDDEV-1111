from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=100)
    mobile = models.CharField(max_length=20)
    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    landmark = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=6)
    is_default = models.BooleanField(default=False)
    # created_at = models.DateTimeField(auto_now_add=True,default=True)
    # ADD THIS FIELD
    is_selected = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.fullname} - {self.city}"

    def save(self, *args, **kwargs):
        # If setting this address as default, unset others
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

    def _str_(self):
        return f"{self.fullname} - {self.address1}, {self.city}"
