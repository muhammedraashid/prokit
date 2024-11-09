from django.urls import path
from . import views

urlpatterns =[
     path('categories/toggle/<int:category_id>/', views.category_list_unlist, name='category_list_unlist'),
     path('categories/edit/<int:category_id>/', views.category_edit, name='category_edit'),
     path('categories/add/', views.category_add, name='category_add'),
]