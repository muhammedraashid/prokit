from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

# Create your models here.

# class UserManager(BaseUserManager):
#     def create_user(self, username, email, password):
#         if not email:
#             raise ValueError("Users must have an email address")
#         if not username:
#             raise ValueError("User must have an username")
        
#         email = self.normalize_email(email)  # Normalize email
#         user = self.model(username=username, email=email)  # Create user instance
#         user.set_password(password) 
#         user.save(using=self._db)
    
#     def create_superuser(self, username, email, password=None):
#         user = self.create_user(username, email, password)  # Create regular user first
#         user.is_admin = True  # Set admin status
#         user.is_staff = True  # Allow access to admin interface
#         user.save(using=self._db)  # Save user with admin status
#         return user
        

# class User(AbstractBaseUser,PermissionsMixin):
#     id = models.AutoField(primary_key=True)
#     username = models.CharField(max_length=150, unique=True)
#     email =  models.EmailField(unique=True)
#     first_name = models.CharField(max_length=30)
#     last_name = models.CharField(max_length=30)
#     is_block = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     last_login = models.DateTimeField(auto_now=True)

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['username','email','first_name','last_name']

#     objects = UserManager()

#     def __str__(self):
#         return self.username