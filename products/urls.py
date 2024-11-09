from django.urls import path
from . import views 

urlpatterns = [
        
  
    path('products/details/<int:variant_id>/', views.userProductView, name='user_product_view'),
    path('shop/',views.Shop,name='user_shop'),

    path('details/<int:product_id>', views.adminProductView, name='admin_product_view'),
    path('add-product/', views.add_product, name='add_product'), 
    path('product/update/<int:product_id>', views.update_product, name='product_edit'),
    path('products/delete/<int:product_id>', views.delete_product, name='delete_products'), 
    path("list-unlist-product/<int:product_id>/", views.list_unlist_product, name='list_unlist_product'),
    path("del_product/<int:product_id>/", views.del_product, name='del_product'),
    
    path('variant/update/<int:variant_id>', views.update_variant, name='variant_edit'),
    path('variant/add/<int:product_id>', views.add_variant, name='add_variant'),
    path('variant/adel/<int:variant_id>', views.delete_variant, name='delete_variant'),


 
]
   