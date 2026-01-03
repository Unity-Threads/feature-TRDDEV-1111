from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from cartPage.models import CartItem,TaxesAndCharges
from address.models import Address  # adjust paths if needed
from decimal import Decimal, ROUND_HALF_UP
import json
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import json

from decimal import Decimal, ROUND_HALF_UP
import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from decimal import Decimal, ROUND_HALF_UP
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
import json


@login_required
def confirm_order(request):

    # --------------------------------------------------
    # STEP 1: AJAX POST FROM CART PAGE
    # (ONLY STORE DATA — NO ORDER CREATION)
    # --------------------------------------------------
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            selected_items = data.get("selected_items", [])
            selected_address_id = data.get("selected_address")
            payment_method = data.get("payment_method")

            if not selected_items or not payment_method:
                return JsonResponse({"error": "Invalid data"}, status=400)

            # Store in session
            request.session["selected_items"] = selected_items
            request.session["selected_address"] = selected_address_id
            request.session["payment_method"] = payment_method

            # ALWAYS redirect to confirm page
            return JsonResponse({
                "redirect_url": reverse("confirm_order")
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    # --------------------------------------------------
    # STEP 2: CONFIRM ORDER PAGE (GET)
    # --------------------------------------------------
    selected_items = request.session.get("selected_items")
    selected_address_id = request.session.get("selected_address")
    payment_method = request.session.get("payment_method")

    if not selected_items:
        return redirect("cart")

    cart_items = CartItem.objects.filter(
        user=request.user,
        id__in=selected_items
    )

    if not cart_items.exists():
        return redirect("cart")

    # ---------------- PRICE CALCULATION ----------------
    tax_obj = TaxesAndCharges.objects.first()
    tax_rate = Decimal(tax_obj.tax) if tax_obj else Decimal("0.00")
    delivery_charge = Decimal(tax_obj.delivery_charges) if tax_obj else Decimal("0.00")
    min_free_delivery = Decimal(tax_obj.min_amount_for_free_delivery) if tax_obj else Decimal("0.00")

    subtotal = sum(Decimal(item.product.price) * item.quantity for item in cart_items)
    taxes = (subtotal * tax_rate / Decimal("100")).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    if subtotal >= min_free_delivery:
        delivery_charge = Decimal("0.00")

    total_price = (subtotal + taxes + delivery_charge).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    # ---------------- ADDRESS ----------------
    selected_address = Address.objects.filter(
        user=request.user,
        id=selected_address_id
    ).first() or Address.objects.filter(
        user=request.user,
        is_default=True
    ).first()

    context = {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "taxes": taxes,
        "delivery_charge": delivery_charge,
        "total_price": total_price,
        "selected_address": selected_address,
        "payment_method": payment_method,
    }

    return render(request, "orders/confirm_order.html", context)


from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.db import transaction
from decimal import Decimal
from django.contrib import messages
from orders.utils import generate_order_code
@login_required
@transaction.atomic
def place_confirm_order(request):
    if request.method != "POST":
        return redirect("cart")

    user = request.user

    # -----------------------------
    # DATA FROM SESSION
    # -----------------------------
    selected_items = request.session.get("selected_items", [])
    selected_address_id = request.session.get("selected_address")
    payment_method = request.session.get("payment_method")

    if not selected_items or payment_method != "cod":
        messages.error(request, "Invalid order request.")
        return redirect("cart")

    # -----------------------------
    # FETCH ADDRESS
    # -----------------------------
    address = Address.objects.filter(user=user, id=selected_address_id).first()
    if not address:
        messages.error(request, "Delivery address not found.")
        return redirect("cart")

    # -----------------------------
    # FETCH CART ITEMS
    # -----------------------------
    cart_items = CartItem.objects.select_related(
        "product", "size"
    ).filter(user=user, id__in=selected_items)

    if not cart_items.exists():
        messages.error(request, "Cart items not found.")
        return redirect("cart")

    # -----------------------------
    # PRICE CALCULATION
    # -----------------------------
    tax_obj = TaxesAndCharges.objects.first()
    tax_rate = Decimal(tax_obj.tax) if tax_obj else Decimal("0.00")
    delivery_charge = Decimal(tax_obj.delivery_charges) if tax_obj else Decimal("0.00")
    min_free_delivery = Decimal(tax_obj.min_amount_for_free_delivery) if tax_obj else Decimal("0.00")

    subtotal = sum(item.price * item.quantity for item in cart_items)
    taxes = (subtotal * tax_rate / Decimal("100")).quantize(Decimal("0.01"))

    if subtotal >= min_free_delivery:
        delivery_charge = Decimal("0.00")

    total_amount = (subtotal + taxes + delivery_charge).quantize(Decimal("0.01"))

    # -----------------------------
    # CREATE ORDER
    # -----------------------------

    order = Order.objects.create(
        user=user,
        address=address,
        payment_method="COD",
        payment_status="PENDING",
        total_amount=total_amount,
        tax_amount=taxes,
        delivery_charges=delivery_charge,
        status="CONFIRMED",
        order_code=generate_order_code(),  # ✅ ORDER CODE HERE

    )

    # -----------------------------
    # CREATE ORDER ITEMS + STOCK REDUCE
    # -----------------------------
    for item in cart_items:
        stock = ProductStock.objects.select_for_update().filter(
            product=item.product,
            size=item.size
        ).first()

        if not stock or stock.stock < item.quantity:
            messages.error(request, f"Insufficient stock for {item.product.name}")
            raise Exception("Stock issue")

        stock.stock -= item.quantity
        stock.save()

        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.price,
            size=item.size,

        )

    # -----------------------------
    # CLEAR CART
    # -----------------------------
    cart_items.delete()

    # -----------------------------
    # CLEAR ONLY CHECKOUT SESSION DATA
    # -----------------------------
    for key in ["selected_items", "selected_address", "payment_method"]:
        request.session.pop(key, None)

    # -----------------------------
    # SUCCESS
    # -----------------------------
    return redirect("order_success")



@login_required
def payment_success(request):
    request.session.pop("payment_method", None)
    return redirect("order_success")


############################ by vasu

@login_required
def order_success(request):
    latest_order = Order.objects.filter(user=request.user).latest("created_at")
    return render(request, "orders/order_success.html", {
        "order": latest_order
    })

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


# orders/views.py

@login_required
def order_detail(request, order_code):
    order = get_object_or_404(
        Order,
        order_code=order_code,
        user=request.user
    )

    items = order.items.all()
    # Check if all items are delivered
    items_statuses = [item.status for item in items]

    # Case 1: All items delivered
    all_delivered = all(status == 'delivered' for status in items_statuses)

    # Case 2: At least one item returned (successfully)
    any_returned = any(status == 'returned' for status in items_statuses)

    # Case 3: Entire order cancelled
    all_cancelled = all(status == 'cancelled' for status in items_statuses)

    # FINAL INVOICE CONDITION
    enable_invoice = all_delivered or any_returned or all_cancelled

    return render(request, 'orders/order_detail.html', {
        'order': order,
            "enable_invoice": enable_invoice,
        'items': items,
    })

@login_required
def load_active_item(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id, order__user=request.user)
    return render(request, "orders/partials/active_item.html", {"item": item})




# orders/views.py
from django.http import JsonResponse
from django.db import transaction

@login_required
def cancel_order_item(request, item_id):
    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "Invalid request method."
        })

    order_item = get_object_or_404(
        OrderItem,
        id=item_id,
        order__user=request.user
    )

    if order_item.status not in ["confirmed", "processing"]:
        return JsonResponse({
            "success": False,
            "message": "This item cannot be cancelled."
        })

    with transaction.atomic():

        # 1️⃣ Mark item cancelled
        order_item.status = "cancelled"
        order_item.save(update_fields=["status"])

        # 2️⃣ Restore stock
        if order_item.product:
            if order_item.size:
                stock = order_item.product.stocks.filter(
                    size=order_item.size
                ).first()
                if stock:
                    stock.stock += order_item.quantity
                    stock.save(update_fields=["stock"])
            else:
                order_item.product.stock += order_item.quantity
                order_item.product.save(update_fields=["stock"])

        # 3️⃣ Recalculate order totals (MODEL METHOD)
        totals = order_item.order.recalculate_totals()

    return JsonResponse({
        "success": True,
        "message": "Item cancelled successfully.",
        "item_id": order_item.id,
        "totals": totals
    })
##### RETURN FUNCTIONALITIES  #######33
@login_required
def item_issue(request, item_id):
    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "Invalid request method."
        })

    order_item = get_object_or_404(
        OrderItem,
        id=item_id,
        order__user=request.user
    )

    if order_item.status != "delivered":
        return JsonResponse({
            "success": False,
            "message": "This item cannot be returned."
        })

    reason = request.POST.get("reason", "").strip()
    if not reason:
        return JsonResponse({
            "success": False,
            "message": "Please provide a return reason."
        })

    with transaction.atomic():

        # 1️⃣ Mark as returned
        order_item.status = "returned"
        order_item.return_reason = reason
        order_item.refunded_quantity = order_item.quantity
        order_item.save(update_fields=[
            "status",
            "return_reason",
            "refunded_quantity"
        ])

        # 2️⃣ Restore stock
        if order_item.product:
            if order_item.size:
                stock = order_item.product.stocks.filter(
                    size=order_item.size
                ).first()
                if stock:
                    stock.stock += order_item.quantity
                    stock.save(update_fields=["stock"])
            else:
                order_item.product.stock += order_item.quantity
                order_item.product.save(update_fields=["stock"])

        # 3️⃣ Recalculate order totals
        totals = order_item.order.recalculate_totals()

    return JsonResponse({
        "success": True,
        "message": "Item returned successfully.",
        "item_id": order_item.id,
        "totals": totals
    })#### EMAIL SERVICE #####

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


# orders/views.py
from django.shortcuts import render, get_object_or_404
from .models import OrderItem

def track_order_item(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id)
    return render(request, 'orders/track_order_item.html', {
        'item': item
    })


