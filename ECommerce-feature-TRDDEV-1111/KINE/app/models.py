from django.db import models

# Size model
class Size(models.Model):
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=5, blank=True, null=True)

    ORDER = ["XS", "S", "M", "L", "XL", "XXL", "XXXL"]

    class Meta:
        ordering = []  # remove default ordering

    def order_index(self):
        try:
            return self.ORDER.index(self.code)
        except ValueError:
            return 999  # unknown size goes last

    def __str__(self):
        return self.code or self.name

# Season model
class Season(models.Model):
    name = models.CharField(max_length=50, unique=True)  # Summer, Winter, Spring, Fall

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    image_url = models.URLField(max_length=500, blank=True, null=True)  # Changed from ImageField to URLField
    price = models.DecimalField(max_digits=10, decimal_places=2)
    color = models.CharField(max_length=50, blank=True, null=True)  # e.g., Red, Blue, Black
    is_available_for_cod = models.BooleanField(default=True)
    season = models.ForeignKey('Season', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# Stock per product & size
class ProductStock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stocks')
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('product', 'size')  # one stock entry per size per product

    def __str__(self):
        return f"{self.product.name} - {self.size.name} ({self.stock})"



# ✅ New: Multiple images model
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField(max_length=500, blank=True, null=True)  # Changed from ImageField to URLField
    alt_text = models.CharField(max_length=255, blank=True, null=True)
    is_feature = models.BooleanField(default=False)  # Optionally mark one image as main

    def __str__(self):
        return f"{self.product.name} - Image {self.id}"


