
from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import handler404,handler500
from users.views import custom_404_view ,custom_500_view

urlpatterns = [
    path("admin_panel/", admin.site.urls), 

    path('admin/',include('admin_panel.urls')),
    path('',include('users.urls')),
    path('products/',include('products.urls')),
    path('categories/',include('categories.urls')),
    path('coupon/',include('coupon.urls')),
    path('cart/',include('cart.urls')),
    path('address/',include('address.urls')),
    path('order/',include('order_management.urls')),
    path('wishlist/',include('wishlist.urls')),
    path('wallet/',include('wallet.urls')),

    
    path('accounts/', include('allauth.urls')), 
 
]

handler404 = custom_404_view
handler500 = custom_500_view 

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)