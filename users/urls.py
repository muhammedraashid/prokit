
from django.urls import path
from users import views

urlpatterns = [
    path('',views.UserSignIn,name='user_signin'),
    path('signin/',views.UserSignIn,name='user_signin'),
    path('signup/',views.UserSignUp,name='user_signup'),
    path('home/',views.Home,name='home'),

    path('home/logout/',views.userLogout,name='user_logout'),
    
    # path('product/',views.Home,name='product'),
    #forgot password 
    path('password-reset/', views.initiate_password_reset, name='initiate_password_reset'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),

   
    
]
