
from django.urls import path
from . import views



urlpatterns = [
  path('signin/',views.adminSignIn,name='admin_signin'),
  path('dashboard/',views.adminDashboard,name='admin_dashboard'),
  path('users/',views.adminUsers,name='admin_users'),
  path('products/',views.adminProducts,name='admin_products'),
  path('categories/',views.adminCategories,name='admin_categories'),

  path('logout',views.adminLogout,name='admin_logout'),

  path('users/toggle/<int:user_id>/', views.user_block_unblock, name='user_block_unblock'),

]
