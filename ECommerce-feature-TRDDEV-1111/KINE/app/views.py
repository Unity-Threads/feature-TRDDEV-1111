from django.shortcuts import render,redirect,get_object_or_404

from .models import *
def product_list(request):
    # Fetch all products
    products = Product.objects.all()
    # Pass products to template
    return render(request, 'app/product_list.html', {'products': products})



from wishlist.models import Wishlist

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

    return render(request, 'app/product_detail.html', {
        'product': product,
        'wishlist_ids': wishlist_ids,
        "stocks": sorted_stocks
    })
