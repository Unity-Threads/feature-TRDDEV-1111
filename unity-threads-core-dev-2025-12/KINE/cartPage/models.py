from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
class TaxesAndCharges(models.Model):
    tax = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    delivery_charges = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    min_amount_for_free_delivery = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    def __str__(self):
        return f"TaxesAndCharges (Tax: {self.tax}%, Delivery: {self.delivery_charges}, Min Free Delivery: {self.min_amount_for_free_delivery})"
from app.models import Product,Size

class CartItem(models.Model):
    # Link cart item to a specific user
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items', null=True, blank=True)
    # ADD THIS FIELD
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    image_url = models.URLField(max_length=500)   # URL of the product image
    name = models.CharField(max_length=200)       # Product name
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Product price
    color = models.CharField(max_length=50)       # Color of the product
    size = models.ForeignKey(Size, null=True, on_delete=models.SET_NULL)
    quantity = models.PositiveIntegerField(default=1)  # Quantity in cart
    is_available_for_cod = models.BooleanField(default=True)
    stock = models.PositiveIntegerField(default=0)  # Available stock for this item
    def subtotal(self):
        """Return total price for this cart item"""
        return self.price * self.quantity

    def __str__(self):
        user_info = f"{self.user.username}'s" if self.user else "Guest"
        return f"{user_info} CartItem: {self.name} ({self.quantity}) - Size: {self.size} - Stock: {self.stock}"

