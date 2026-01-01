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
