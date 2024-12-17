from django.urls import path
from . import views

urlpatterns = [
    path('items/', views.wishlist, name='wishlist'),
    path('add-to-wishlist/<slug:variant_size_slug>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove-from-wishlist/<slug:variant_size_slug>/', views.remove_from_wishlist, name='remove_from_wishlist'),

]