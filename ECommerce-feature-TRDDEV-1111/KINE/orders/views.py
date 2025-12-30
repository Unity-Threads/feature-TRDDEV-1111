from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from cartPage.models import CartItem,TaxesAndCharges
from address.models import Address  # adjust paths if needed
from decimal import Decimal, ROUND_HALF_UP

from django.http import JsonResponse
from django.urls import reverse
@login_required
def confirm_order(request):

    # ⭐ CASE 1 — AJAX POST from JavaScript
    if request.method == "POST":
        return JsonResponse({
            "redirect_url": reverse("confirm_order")
        })

    # ⭐ CASE 2 — Normal GET request (for page load)
    selected_address_id = request.GET.get("selected_address")

    # ⭐⭐⭐ ADD THIS BLOCK — Update selected address in DB ⭐⭐⭐
    if selected_address_id and selected_address_id.isdigit():
        Address.objects.filter(user=request.user, is_selected=True).update(is_selected=False)
        Address.objects.filter(id=selected_address_id, user=request.user).update(is_selected=True)

    items_param = request.GET.get("items")

    if items_param:
        item_ids = [int(i) for i in items_param.split(",") if i.isdigit()]
        cart_items = CartItem.objects.filter(user=request.user, id__in=item_ids)
    else:
        cart_items = CartItem.objects.filter(user=request.user)

    if not cart_items.exists():
        return redirect("product_list")

    # ⭐ TAX
    tax_obj = TaxesAndCharges.objects.first()

    if tax_obj:
        tax_rate = Decimal(tax_obj.tax)
        delivery_charge = Decimal(tax_obj.delivery_charges)
        min_free_delivery = Decimal(tax_obj.min_amount_for_free_delivery)
    else:
        tax_rate = Decimal("0.00")
        delivery_charge = Decimal("0.00")
        min_free_delivery = Decimal("0.00")

    subtotal = sum(Decimal(item.product.price) * item.quantity for item in cart_items)

    taxes = (subtotal * tax_rate / Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    if subtotal >= min_free_delivery:
        delivery_charge = Decimal("0.00")

    total_price = (subtotal + taxes + delivery_charge).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    # ⭐ GET SELECTED ADDRESS
    selected_address = Address.objects.filter(user=request.user, is_selected=True).first()
    if not selected_address:
        selected_address = Address.objects.filter(user=request.user, is_default=True).first()

    context = {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "taxes": taxes,
        "delivery_charge": delivery_charge,
        "total_price": total_price,
        "selected_address": selected_address,
        "tax_rate": tax_rate,
        "min_free_delivery": min_free_delivery,
    }

    return render(request, "orders/confirm_order.html", context)

# views.py
from django.shortcuts import render, redirect
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import razorpay
from django.contrib.auth.decorators import login_required
# from cart.models import Cart

from orders.models import  Order

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@login_required
def razorpay_payment(request):
    if request.method == "POST":
        user = request.user
        cart_items = CartItem.objects.filter(user=user)

        if not cart_items.exists():
            return redirect('cart')

        total_price = sum(item.product.price * item.quantity for item in cart_items)
        amount = int(total_price * 100)  # convert to paise

        # Razorpay client
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        # Create Razorpay order
        razorpay_order = client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": "1"
        })

        # ✅ Create Order records in your DB (for each cart item)
        for item in cart_items:
            Order.objects.create(
                user=user,
                product=item.product,
                size=item.size,  # or item.size.code
                quantity=item.quantity,
                total_price=item.product.price * item.quantity,
                payment_method='razorpay',
                status='pending',
                razorpay_order_id=razorpay_order['id']
            )

        context = {
            'cart_items': cart_items,
            'amount': amount,
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'total_price': total_price,
        }

        return render(request, 'orders/razorpay_payment.html', context)

    return redirect('cart')



# views.py
@csrf_exempt
def razorpay_success(request):
    if request.method == "POST":
        # Update order status, clear cart, etc.
        return render(request, 'orders/payment_success.html')
    return redirect('cart')


from django.shortcuts import render
from orders.models import Order

def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_history.html', {'orders': orders})


