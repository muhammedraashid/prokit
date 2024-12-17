"""
URL configuration for prokit project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("admin_panel/", admin.site.urls), # built-in

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

    
    path('accounts/', include('allauth.urls')),  # Allauth URLs
 
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)