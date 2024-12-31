from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


# Create your models here.

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    street_address = models.CharField(max_length=300)
    pincode = models.CharField(max_length=20)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    is_default = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
  
    def soft_delete(self):
        self.is_deleted = True
        self.save()

        
    def __str__(self):
        return f"{self.name} - {self.street_address},{self.pincode}"