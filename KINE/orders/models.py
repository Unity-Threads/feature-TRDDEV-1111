from django.db import models
from django.conf import settings
from address.models import Address
from app.models import Product, Size
import uuid


# =========================
# ORDER
# =========================
class Order(models.Model):

    # ---------- Order Identity ----------
    order_code = models.CharField(max_length=12, unique=True, editable=False)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)

    # ---------- Amounts ----------
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # ---------- Payment ----------
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )

    payment_method = models.CharField(max_length=50, default="razorpay")
    razorpay_order_id = models.CharField(max_length=200, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=200, null=True, blank=True)
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default='pending'
    )

    # ---------- Order Status ----------
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out For Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('returned', 'Returned'),
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # ---------- Timestamps ----------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.order_code:
            self.order_code = uuid.uuid4().hex[:12].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_code

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_code']),
            models.Index(fields=['user']),
            models.Index(fields=['created_at']),
        ]


# =========================
# ORDER ITEM
# =========================
class OrderItem(models.Model):

    STATUS_CHOICES = (
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out For Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('returned', 'Returned'),
    )

    order = models.ForeignKey(
        Order,
        related_name="items",
        on_delete=models.CASCADE
    )

    # ---------- Product Snapshot ----------
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=255,null=True)
    product_sku = models.CharField(max_length=100, blank=True)

    size = models.ForeignKey(Size, null=True, blank=True, on_delete=models.SET_NULL)

    quantity = models.PositiveIntegerField(default=1)
    refunded_quantity = models.PositiveIntegerField(default=0)

    price = models.DecimalField(max_digits=10, decimal_places=2)  # per item price snapshot

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='confirmed'
    )

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"


# =========================
# RATING (Verified Purchase)
# =========================
class Rating(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order_item = models.OneToOneField(OrderItem, on_delete=models.CASCADE,default=None)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    stars = models.PositiveIntegerField()  # 1 to 5
    review = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.stars}⭐ - {self.product}"


# =========================
# RETURN REQUEST
# =========================
class ReturnRequest(models.Model):

    STATUS_CHOICES = (
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('picked_up', 'Picked Up'),
        ('refunded', 'Refunded'),
    )

    item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    reason = models.CharField(max_length=250)
    quantity = models.PositiveIntegerField(default=1)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='requested'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Return {self.item} ({self.status})"
