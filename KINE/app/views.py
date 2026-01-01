from django.shortcuts import render,redirect,get_object_or_404

from .models import *

from django.shortcuts import render
from .models import Product, ProductStock

def shop(request):

    products = Product.objects.all()

    category = request.GET.get("category")
    season = request.GET.get("season")
    product_type = request.GET.get("type")
    color = request.GET.get("color")
    size = request.GET.get("size")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")


    if category:
        products = products.filter(category__name=category)

    if season:
        products = products.filter(season__name=season)

    if product_type:
        products = products.filter(product_type__name=product_type)

    if color:
        products = products.filter(color__iexact=color)

    if size:
        products = products.filter(stocks__size__code=size, stocks__stock__gt=0)

    if min_price:
        products = products.filter(price__gte=min_price)

    if max_price:
        products = products.filter(price__lte=max_price)

    context = {

        "products": products,
        "categories": Category.objects.all(),
        "product_types": ProductType.objects.all(),
        "seasons": Season.objects.all(),
        "sizes": Size.objects.all(),
        "colors": Product.objects.values_list("color", flat=True).distinct(),
    }

    return render(request, "app/shop.html", context)

def category_shop(request):

    products = Product.objects.all()

    category = request.GET.get("category")

    if category:
        products = products.filter(category__name=category)

    context = {
        "products": products,
        "categories": Category.objects.all(),
    }

    return render(request, "app/category_shop.html", context)


def producttype_shop(request):

    products = Product.objects.all()

    product_type = request.GET.get("type")

    if product_type:
        products = products.filter(product_type__name=product_type)

    context = {
        "products": products,
        "product_types": ProductType.objects.all(),
    }

    return render(request, "app/product_type_shop.html", context)
def accessories_shop(request):

    products = Product.objects.filter(product_type__name="Accessories")

    context = {
        "products": products,
    }

    return render(request, "app/accessories_shop.html", context)


def product_list(request):
    # Fetch all products
    products = Product.objects.all()
    # Pass products to template
    return render(request, 'app/product_list.html', {'products': products})


# from cartPage.models import CartItem
from wishlist.models import Wishlist
from cartPage.models import CartItem

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    sorted_stocks = sorted(
        product.stocks.all(),
        key=lambda s: s.size.order_index()
    )

    # Get wishlist items for this user
    if request.user.is_authenticated:
        wishlist_ids = list(
            Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
        )
    else:
        wishlist_ids = []



    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(
            user=request.user,
            product=product
        ).values_list("size", flat=True)
    else:
        cart_items = []

    return render(request, 'app/product_detail.html', {
        'product': product,
        'wishlist_ids': wishlist_ids,
        "stocks": sorted_stocks,
        "cart_size_ids": list(cart_items)
    })
