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
        path("active-item/<int:item_id>/", views.load_active_item, name="load_active_item"),
        path(
                "item/<int:item_id>/cancel/",
                views.cancel_order_item,
                name="cancel_order_item"
        ),
        path('item/<int:item_id>/track/', views.track_order_item, name='track_order_item'),
        path("success/", views.order_success, name="order_success"),
        path(
            "place-confirm-order/",
            views.place_confirm_order,
            name="place_confirm_order"
)

]