from django.contrib import admin
from django.utils.html import format_html
from . models import *
# Register your models here.

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'get_product_price', 'get_product_image','product_image')
    list_filter = ('user',)
    search_fields = ('user__username', 'product__name')
    ordering = ('-id',)

    def get_product_price(self, obj):
        return obj.product.price
    get_product_price.short_description = 'Product Price'

    def get_product_image(self, obj):
        return obj.product.image_url if obj.product.image_url else 'No Image'
    get_product_image.short_description = 'Image URL'

    def product_image(self, obj):
        if obj.product.image_url:
            return format_html('<img src="{}" width="50" height="50" style="border-radius:5px;"/>', obj.product.image_url)
        return "No Image"
    product_image.short_description = 'Image'
