from django.urls import path
from . import views


urlpatterns = [
    path('coupons/', views.coupons, name='admin_coupons'),
    path('coupons/create/', views.create_coupon, name='create_coupon'),
    path('coupons/remove/<int:coupon_id>/', views.remove_coupon, name='remove_coupon'),
]
