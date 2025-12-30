from django.urls import path
from . import views

urlpatterns = [

        path('confirm_order/', views.confirm_order, name='confirm_order'),
        path('razorpay-payment/', views.razorpay_payment, name='razorpay_payment'),
        path('razorpay-success/', views.razorpay_success, name='razorpay_success'),
        path('order-history/', views.order_history, name='order_history'),
]