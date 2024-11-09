from django.db import models

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=60) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_listed = models.BooleanField(default=True)

    def __str__(self):
        return self.name
