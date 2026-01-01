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


from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import razorpay
from datetime import datetime

from cartPage.models import CartItem
from orders.models import Order, OrderItem
from orders.utils import send_order_confirmation_email
from app.models import Product, Size, ProductStock

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@login_required
def razorpay_payment(request):
    if request.method != "POST":
        return redirect("cartPage")

    user = request.user

    # 🟦 Selected Address
    selected_address_id = request.POST.get("selected_address")
    selected_address = None

    if selected_address_id:
        selected_address = Address.objects.filter(id=selected_address_id, user=user).first()

    # 🟦 Fetch Cart Items
    cart_items = CartItem.objects.filter(user=user)
    if not cart_items.exists():
        return redirect("cartPage")

    # 🟦 Subtotal
    subtotal = sum(float(item.price) * item.quantity for item in cart_items)

    # 🟦 Taxes & Delivery from DB
    tax_obj = TaxesAndCharges.objects.first()
    tax_percentage = float(tax_obj.tax)
    delivery_charges = float(tax_obj.delivery_charges)
    free_delivery_min = float(tax_obj.min_amount_for_free_delivery)

    # 🟦 Tax Calculation
    tax_amount = round((subtotal * tax_percentage) / 100, 2)

    # 🟦 Delivery Logic
    final_delivery = 0 if subtotal >= free_delivery_min else delivery_charges

    # 🟦 Grand Total
    grand_total = subtotal + tax_amount + final_delivery

    # Razorpay uses paise
    amount_paise = int(grand_total * 100)

    # 🟦 Create Razorpay Order
    razorpay_order = client.order.create({
        "amount": amount_paise,
        "currency": "INR",
        "payment_capture": 1
    })

    # 🟦 Generate Order Code
    year_suffix = datetime.now().strftime("%y")
    last_order = Order.objects.filter(
        order_code__startswith=f"UT{year_suffix}"
    ).order_by("id").last()

    if last_order:
        last_seq = int(last_order.order_code[4:])
        new_seq = last_seq + 1
    else:
        new_seq = 1

    order_code = f"UT{year_suffix}{new_seq:06d}"

    # 🟦 Create Order
    order = Order.objects.create(
        user=user,
        order_code=order_code,
        address=selected_address,
        total_amount=subtotal,
        tax_amount=tax_amount,
        delivery_charges=final_delivery,
        grand_total=grand_total,
        payment_method="razorpay",
        status="pending",
        razorpay_order_id=razorpay_order["id"],
    )

    # 🟦 Create Order Items (IMPORTANT)
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            size=item.size,  # Size instance (NOT "S"/"M")
            quantity=item.quantity,
            price=float(item.price)
        )

    # 🟦 Clear Cart after creating order items
    cart_items.delete()

    # 🟦 Send to Template
    context = {
        "order": order,
        "razorpay_order_id": razorpay_order["id"],
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,

        "subtotal": subtotal,
        "tax_amount": tax_amount,
        "delivery_charge": final_delivery,
        "grand_total": grand_total,
        "selected_address": selected_address,
        "amount_paise": amount_paise,
    }

    return render(request, "orders/razorpay_payment.html", context)


# ------------------- Payment Success Handler -------------------
@csrf_exempt
def razorpay_payment_success(request):
    if request.method == "POST":
        data = request.POST

        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_signature = data.get('razorpay_signature')

        # Fetch the order
        order = get_object_or_404(Order, razorpay_order_id=razorpay_order_id)

        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        try:
            client.utility.verify_payment_signature(params_dict)

            # Update order status
            order.status = 'paid'
            order.razorpay_payment_id = razorpay_payment_id
            order.razorpay_signature = razorpay_signature
            order.save()

            # -------------------------------
            #  STOCK DEDUCTION (SOLUTION 2)
            # -------------------------------

            for item in order.items.all():
                try:
                    # item.size is already a Size instance (if ForeignKey)
                    size_obj = item.size

                    # Get stock entry
                    stock_entry = ProductStock.objects.get(
                        product=item.product,
                        size=size_obj
                    )

                    # Deduct stock
                    if stock_entry.stock >= item.quantity:
                        stock_entry.stock -= item.quantity
                        stock_entry.save()
                    else:
                        print(f"Stock not sufficient for {item.product.name} ({size_obj.code})")

                except ProductStock.DoesNotExist:
                    print(f"No ProductStock entry for {item.product.name} - {size_obj.code}")
            # -------------------------------
            # Send confirmation email
            # -------------------------------
            send_order_confirmation_email(order)

            return render(request, 'orders/payment_success.html', {
                'order': order,
                'status': 'success'
            })

        except razorpay.errors.SignatureVerificationError:
            order.status = 'failed'
            order.save()

            return render(request, 'orders/payment_success.html', {
                'order': order,
                'status': 'failed'
            })

    return redirect('cartPage')


from django.shortcuts import render
from orders.models import Order
# orders/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Order


@login_required
def order_history(request):
    orders = (
        Order.objects
        .filter(user=request.user)
        .prefetch_related('items')
        .order_by('-created_at')
    )

    return render(request, 'orders/order_history.html', {
        'orders': orders
    })
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import OrderItem, ReturnRequest

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from orders.models import OrderItem, ReturnRequest
from app.models import Product, ProductStock  # Assuming you have Stock model for sizes

@login_required
def item_issue(request, item_id):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request method."})

    reason = request.POST.get("reason", "").strip()
    if not reason:
        return JsonResponse({"success": False, "message": "Please provide a reason."})

    order_item = get_object_or_404(OrderItem, id=item_id, order__user=request.user)

    if order_item.status != "delivered":
        return JsonResponse({"success": False, "message": "Only delivered items can be returned."})

    # Create ReturnRequest
    ReturnRequest.objects.create(
        item=order_item,
        reason=reason,
        status="requested"
    )

    # Update order item status
    order_item.status = "returned"
    order_item.save()

    # Increase stock
    if order_item.size:
        stock_obj = order_item.product.stocks.filter(size=order_item.size).first()
        if stock_obj:
            stock_obj.stock += order_item.quantity
            stock_obj.save()
    else:
        order_item.product.stock += order_item.quantity
        order_item.product.save()

    return JsonResponse({"success": True, "message": "Return request submitted and stock updated!"})


from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from app.models import Product, Size
from .models import OrderItem, Order

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from app.models import Product, Size
from .models import OrderItem, Order

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

@login_required
def cancel_order_item(request, item_id):
    # AJAX expects GET
    if request.method != "GET":
        return JsonResponse({"success": False, "message": "Invalid request method."})

    order_item = get_object_or_404(OrderItem, id=item_id, order__user=request.user)

    if order_item.status not in ['confirmed', 'processing']:
        return JsonResponse({"success": False, "message": "Cannot cancel this item now."})

    order_item.status = 'cancelled'
    order_item.save()

    # Update stock if using size
    if order_item.size:
        stock_obj = order_item.product.stocks.filter(size=order_item.size).first()
        if stock_obj:
            stock_obj.stock += order_item.quantity
            stock_obj.save()
    else:
        order_item.product.stock += order_item.quantity
        order_item.product.save()

    # Update order totals
    order = order_item.order
    order.total_amount -= order_item.price * order_item.quantity
    order.grand_total = order.total_amount + order.tax_amount + order.delivery_charges
    order.save()

    return JsonResponse({
        "success": True,
        "message": "Item cancelled successfully!",
        "totals": {
            "total_amount": float(order.total_amount),
            "tax_amount": float(order.tax_amount),
            "delivery_charges": float(order.delivery_charges),
            "grand_total": float(order.grand_total),
        }
    })

from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required

@login_required
def order_summary(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    confirmed_items = order.items.filter(status='confirmed')
    cancelled_items = order.items.filter(status='cancelled')

    return render(request, 'orders/order_summary.html', {
        'order': order,
        'confirmed_items': confirmed_items,
        'cancelled_items': cancelled_items,
    })
@login_required

def order_item_detail(request, item_id):
    item = get_object_or_404(
        OrderItem,
        id=item_id,
        order__user=request.user
    )
    return render(request, "orders/order_item_detail.html", {
        "item": item
    })

# orders/views.py
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order

@login_required
def order_detail(request, order_code):
    order = get_object_or_404(
        Order,
        order_code=order_code,
        user=request.user
    )
    return render(request, 'orders/order_detail.html', {
        'order': order
    })


# orders/views.py
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import OrderItem, Order

@login_required
def cancel_order_item(request, item_id):
    """
    Cancel an order item via AJAX:
    - Update status
    - Restore stock
    - Update order totals
    """
    order_item = get_object_or_404(OrderItem, id=item_id, order__user=request.user)
    order = order_item.order

    if order_item.status not in ['confirmed', 'processing']:
        return JsonResponse({'success': False, 'message': 'Cannot cancel this item!'})

    try:
        with transaction.atomic():
            # 1️⃣ Cancel item
            order_item.status = 'cancelled'
            order_item.save()

            # 2️⃣ Restore stock
            if order_item.product:
                if order_item.size:
                    stock_obj = order_item.product.stocks.filter(size=order_item.size).first()
                    if stock_obj:
                        stock_obj.stock += order_item.quantity
                        stock_obj.save()
                else:
                    order_item.product.stock += order_item.quantity
                    order_item.product.save()

            # 3️⃣ Update order totals
            cancelled_amount = order_item.price * order_item.quantity
            order.total_amount -= cancelled_amount
            order.grand_total = order.total_amount + order.tax_amount + order.delivery_charges
            order.save()

            # 4️⃣ Return JSON with updated totals
            return JsonResponse({
                'success': True,
                'message': 'Item cancelled successfully!',
                'totals': {
                    'total_amount': str(order.total_amount),
                    'tax_amount': str(order.tax_amount),
                    'delivery_charges': str(order.delivery_charges),
                    'grand_total': str(order.grand_total)
                }
            })

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


#### EMAIL SERVICE #####

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_order_confirmation_email(order):
    subject = f"Order Confirmation - {order.order_code}"
    html_message = render_to_string('orders/order_confirmation_email.html', {'order': order})
    plain_message = strip_tags(html_message)
    recipient_list = [order.user.email]

    send_mail(
        subject,
        plain_message,
        'MyShop <your-email@gmail.com>',
        recipient_list,
        html_message=html_message,
        fail_silently=False,
    )



##### FILTER AND RATING SECTION  #####


from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import Order

def orders_list(request):
    search = request.GET.get("search", "")
    filter_status = request.GET.get("status", "")
    date_filter = request.GET.get("date", "")

    orders = Order.objects.filter(user=request.user)

    # Search
    if search:
        orders = orders.filter(
            Q(order_code__icontains=search) |
            Q(items__product__name__icontains=search)
        ).distinct()

    # Filter by Status
    if filter_status:
        orders = orders.filter(status=filter_status)

    # Filter by date range
    if date_filter == "last_30":
        orders = orders.filter(created_at__gte=timezone.now() - timedelta(days=30))
    elif date_filter == "last_6m":
        orders = orders.filter(created_at__gte=timezone.now() - timedelta(days=180))
    elif date_filter == "last_1y":
        orders = orders.filter(created_at__gte=timezone.now() - timedelta(days=365))

    context = {"orders": orders}
    return render(request, "orders/orders_list.html", context)






############## cancel order item   ###########3

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

from .models import OrderItem


@login_required
def cancel_order_item(request, item_id):
    item = get_object_or_404(
        OrderItem,
        id=item_id,
        order__user=request.user
    )

    # Allowed statuses for cancellation
    cancellable_statuses = ["confirmed", "processing"]

    if item.status not in cancellable_statuses:
        messages.error(request, "This item cannot be cancelled.")
        return redirect("order_item_detail", item_id=item.id)

    # Cancel item
    item.status = "cancelled"
    item.save()

    messages.success(request, "Order item cancelled successfully.")

    return redirect("order_item_detail", item_id=item.id)




# orders/views.py
from django.shortcuts import render, get_object_or_404
from .models import OrderItem

def track_order_item(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id)
    return render(request, 'orders/track_order_item.html', {
        'item': item
    })
