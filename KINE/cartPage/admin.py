from django.contrib import admin
from .models import CartItem,TaxesAndCharges
@admin.register(TaxesAndCharges)
class TaxesAndChargesAdmin(admin.ModelAdmin):
    list_display = ('tax', 'delivery_charges', 'min_amount_for_free_delivery')
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'color', 'size', 'quantity', 'image_url')
