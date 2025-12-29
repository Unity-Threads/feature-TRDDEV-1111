from django.db import models
from django.conf import settings
from address.models import Address
from app.models import Product, Size
import uuid
from decimal import Decimal


# =========================
# ORDER
# =========================
class Order(models.Model):
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

    # ---------- Methods ----------
    def recalculate_totals(self):
        """
        Recalculate order totals based on active (non-cancelled, non-returned) items
        """
        active_items = self.items.exclude(status__in=['cancelled', 'returned'])
        subtotal = sum(item.price * item.quantity for item in active_items)

        tax = (subtotal * Decimal('0.05')).quantize(Decimal('0.01'))  # 5% tax
        delivery = Decimal('50.00') if subtotal > 0 else Decimal('0.00')
        grand_total = subtotal + tax + delivery

        self.total_amount = subtotal
        self.tax_amount = tax
        self.delivery_charges = delivery
        self.grand_total = grand_total

        # If fully cancelled/returned, mark order cancelled
        if grand_total == 0:
            self.status = 'cancelled'

        # Save updated values
        self.save(update_fields=[
            'total_amount', 'tax_amount', 'delivery_charges', 'grand_total', 'status', 'updated_at'
        ])

        # Return dict for use in AJAX responses
        return {
            "total_amount": float(self.total_amount),
            "tax_amount": float(self.tax_amount),
            "delivery_charges": float(self.delivery_charges),
            "grand_total": float(self.grand_total),
        }

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
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=255, null=True)
    product_sku = models.CharField(max_length=100, blank=True)
    size = models.ForeignKey(Size, null=True, blank=True, on_delete=models.SET_NULL)
    quantity = models.PositiveIntegerField(default=1)
    refunded_quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    return_reason = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Recalculate order totals automatically whenever item changes
        if self.order:
            self.order.recalculate_totals()

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"

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
