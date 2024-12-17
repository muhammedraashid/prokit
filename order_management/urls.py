from django.urls import path
from . import views


urlpatterns = [
    path('order-management/', views.admin_order_management, name='admin_orders'),
    path('order-details/<int:ord_id>', views.admin_order_view, name='admin_order_view'),
    # path('sales-report/', views.sales_report, name='sales_report'),
    path('sales_report/export/', views.export_sales_report, name='sales_report_export'),
    path('delivery-charge/',views.set_delivery_charge, name='set_delivery_charge'),
   
    path('checkout/', views.checkout, name='checkout'),
    path('order-place/', views.place_order, name='order_placed'),
    path('checkout/verify-payment/', views.verify_payment, name='verify_payment'), # razorpay-payment order view
    path('order-success/<str:order_number>/', views.order_success, name='order_success'),
    path('payment-failed/<str:order_number>/', views.payment_failed, name='payment_failed'),
    path('retry_payment/<int:ord_id>',views.retry_payment, name='retry_payment'),

    path('orders/', views.user_orders, name='user_orders'),
    path('ordered-item-details/<int:ord_id>', views.user_order_view, name='user_order_view'),
    path('order-cancel/<int:ord_id>', views.cancel_order, name='cancel_order'),
    path('order-return/<int:ord_id>', views.return_order, name='return_order'),
    path('order-item-cancel/<int:item_id>', views.cancel_order_item, name='cancel_order_item'),
    # path('order-return/<int:item_id>', views.return_order_item, name='return_order_item'),
    path('order-status/<int:ord_id>', views.order_status, name='order_status'),
    path('inoice-export/<int:ord_id>', views.export_invoice, name='export_invoice'),
   
    
    # path('payment-success/', views.payment_success, name='payment_success'), 
    # path('payment-conform/', views.confirm_payment, name='confirm_payment'),
  

   
]