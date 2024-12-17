from django.urls import path
from . import views 

urlpatterns = [
        
  
    path('product/details/<slug:variant_size_slug>/', views.userProductView, name='user_product_view'),
    path('shop/',views.Shop,name='user_shop'),

    path('details/<slug:slug>', views.adminProductView, name='admin_product_view'),
    path('add-product/', views.add_product, name='add_product'), 
    path('product/update/<slug:slug>', views.update_product, name='product_edit'),
    path("list-unlist-product/<slug:slug>/", views.list_unlist_product, name='list_unlist_product'),
    
    path('variant/update/<slug:variant_slug>', views.update_variant, name='variant_edit'),
    path('variant/add/<slug:slug>', views.add_variant, name='add_variant'),
    path('variant/del/<slug:variant_slug>', views.delete_variant, name='delete_variant'),
    path('variant-images-delete/<int:image_id>', views.delete_image, name='delete_image'),



 
]
   