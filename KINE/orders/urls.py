from django.urls import path
from . import views

urlpatterns = [

        path('confirm_order/', views.confirm_order, name='confirm_order'),
        path('razorpay-payment/', views.razorpay_payment, name='razorpay_payment'),
        path('razorpay-success/', views.razorpay_payment_success, name='razorpay_payment_success'),
        path('my-orders/', views.order_history, name='order_history'),
        path('order-detail/<str:order_code>/', views.order_detail, name='order_detail'),
        path("item/<int:item_id>/cancel/", views.cancel_order_item, name="cancel_order_item"),
        path("item/<int:item_id>/return/", views.item_issue, name="item_issue"),
        path('orders/<int:order_id>/summary/', views.order_summary, name='order_summary'),
        path("orders/item/<int:item_id>/",
        views.order_item_detail,
        name = "order_item_detail"),
        path(
                "item/<int:item_id>/cancel/",
                views.cancel_order_item,
                name="cancel_order_item"
        ),
        path('item/<int:item_id>/track/', views.track_order_item, name='track_order_item'),

]