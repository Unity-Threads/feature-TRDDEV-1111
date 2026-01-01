from django.shortcuts import render

# Create your views here.


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Wishlist
from app.models import Product


# views.py
from django.http import JsonResponse
from .models import Wishlist
# views.py
from django.http import JsonResponse
from .models import Wishlist, Product


@login_required
def toggle_wishlist(request, product_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)

    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)

    if not created:
        # Already exists → remove from wishlist
        wishlist_item.delete()
        added = False
    else:
        added = True

    return JsonResponse({'added': added})


@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'wishlist/wishlist.html', {'wishlist_items': wishlist_items})
