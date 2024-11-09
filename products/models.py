from django.db import models
from categories.models import Category
from django.contrib.auth.models import User

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    brand = models.CharField(max_length=30)
    offer = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    is_listed = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
class Variant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    size = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
    stock = models.PositiveIntegerField()
    
    class Meta:
            verbose_name = 'Variant'
            verbose_name_plural = 'Variants'

    def __str__(self):
        return f"{self.product.name} - {self.size} - {self.color}"

class VariantImages(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE,related_name='images')
    image = models.ImageField(upload_to='product_variants/')

    class Meta :
          verbose_name = 'image'
          verbose_name_plural = 'images'
   
   
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    comments = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'

    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.rating}"    

 