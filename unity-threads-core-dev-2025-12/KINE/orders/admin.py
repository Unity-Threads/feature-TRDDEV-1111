from django.contrib import admin
from .models import Order, OrderItem


# --- Inline Order Items inside Order Admin ---
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'size', 'quantity', 'price')
    can_delete = False


# --- Order Admin ---
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_code',
        'user',
        'payment_status',
        'status',
        'grand_total',
        'created_at'
    )

    list_filter = (
        'payment_status',
        'status',
        'payment_method',
        'created_at',
    )

    search_fields = (
        'order_code',
        'user__username',
        'user__email',
        'razorpay_order_id',
        'razorpay_payment_id',
    )

    readonly_fields = (
        'order_code',
        'user',
        'address',
        'total_amount',
        'tax_amount',
        'delivery_charges',
        'grand_total',
        'payment_method',
        'razorpay_order_id',
        'razorpay_payment_id',
        'payment_status',
        'status',
        'created_at',
    )

    inlines = [OrderItemInline]

    fieldsets = (
        ("Order Info", {
            "fields": (
                "order_code",
                "user",
                "address",
                "created_at",
            )
        }),
        ("Amount Details", {
            "fields": (
                "total_amount",
                "tax_amount",
                "delivery_charges",
                "grand_total",
            )
        }),
        ("Payment Details", {
            "fields": (
                "payment_method",
                "payment_status",
                "razorpay_order_id",
                "razorpay_payment_id",
            )
        }),
        ("Order Status", {
            "fields": ("status",)
        }),
    )

