from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


def send_order_confirmation_email(order):
    """
    Sends order confirmation email to the user after successful payment.
    """
    subject = f"Order Confirmation - {order.order_code}"
    recipient = order.user.email
    # Render email template with order context
    message = render_to_string("orders/order_confirmation_email.html", {"order": order})

    send_mail(
        subject,
        message,  # plain text fallback
        settings.DEFAULT_FROM_EMAIL,
        [recipient],
        html_message=message,  # send HTML email
        fail_silently=False,
    )

from orders.models import Order
from datetime import datetime

def generate_order_code():
    year_suffix = datetime.now().strftime("%y")

    last_order = Order.objects.filter(
        order_code__startswith=f"UT{year_suffix}"
    ).order_by("id").last()

    if last_order:
        last_seq = int(last_order.order_code[4:])
        new_seq = last_seq + 1
    else:
        new_seq = 1

    return f"UT{year_suffix}{new_seq:06d}"
