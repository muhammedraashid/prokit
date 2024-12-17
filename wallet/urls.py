from django.urls import path
from . import views

urlpatterns = [
    path('wallet/',views.wallet, name='wallet'),
    path('add-to-wallet/',views.add_to_wallet, name='add_to_wallet')
]
