from django.contrib import admin
from .models import Product, Size, ProductStock, Season , ProductImage

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')

@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('name',)

class ProductStockInline(admin.TabularInline):
    model = ProductStock
    extra = 1

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_available_for_cod', 'season', 'created_at','image_url')
    inlines = [ProductStockInline,ProductImageInline]
    list_filter = ('season',)
    search_fields = ('name',)

@admin.register(ProductStock)
class ProductStockAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'stock')
    list_filter = ('size', 'product')
