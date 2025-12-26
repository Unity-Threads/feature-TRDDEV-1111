from django.db import models

from app.models import Product
# Create your models here.


from django.conf import settings
class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')  # prevent duplicates

    def __str__(self):
        return f"{self.user} → {self.product}"