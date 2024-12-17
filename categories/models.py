from django.db import models
from django.utils.text import slugify


# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=60) 
    offer = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_listed = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Size(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='sizes')
    size = models.CharField(max_length=30)
   
class Color(models.Model):
    name = models.CharField(max_length=50, unique=True)

class Brand(models.Model):
    name = models.CharField(max_length=50, unique=True)