from django.urls import path
from . import views

urlpatterns = [
    path('account/addresses',views.UserAddresses,name='user_addresses'),
    path('account/add-address',views.add_address,name='add_address'),
    # path('checkout/add-address',views.add_address_from_chekout,name='add_address_from_checkout'),

    path('account/delete-address/<int:address_id>', views.delete_address,name='delete_address'),
    path('account/update-address/<int:address_id>',views.update_address, name='update_address')
]