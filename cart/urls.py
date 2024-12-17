from django.urls import path
from . import views

urlpatterns = [
    path('cart/',views.CartView,name='cart'),
    path('cart/add-to-cart/<slug:variant_size_slug>',views.add_to_cart,name='add_to_cart'),
    path('update-cart/', views.update_cart, name='update_cart'),
    # path('update-cart/', views.selected_coupon, name='selected_coupon'),     
    path('remove-cart-item/<int:item_id>', views.remove_from_cart, name='remove_from_cart'),
    path('remove-applied-coupon', views.remove_coupon, name='remove_coupon'),


]