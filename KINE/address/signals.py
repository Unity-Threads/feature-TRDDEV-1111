# address/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from django.core.mail import send_mail
from django.conf import settings

@receiver(post_save, sender=Order)
def order_status_notification(sender, instance, created, **kwargs):
    """
    Sends email notification when an order is placed or status changes.
    """
    subject = ''
    message = ''
    recipient = [instance.user.email]

    if created:
        subject = f"Order #{instance.id} Placed Successfully"
        message = f"Dear {instance.user.username},\n\nYour order has been placed successfully.\nStatus: {instance.status}\n\nThank you for shopping with us!"
    else:
        subject = f"Order #{instance.id} Status Updated"
        message = f"Dear {instance.user.username},\n\nYour order status has been updated to: {instance.status}.\n\nExpected Delivery: {instance.expected_delivery_date}\n\n- Team Techno Forest"

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient, fail_silently=True)
