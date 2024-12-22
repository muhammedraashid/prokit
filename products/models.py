from django.db import models
from categories.models import Category, Size
from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils.text import slugify
from django.utils import timezone

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    brand = models.CharField(max_length=30)
    offer = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    is_listed = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, blank=True)
    # created_at = models.DateTimeField(auto_now_add=True, default=now)


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args,**kwargs)

    def __str__(self):
        return self.name
    
    def average_rating(self):
        reviews = self.reviews.all()  
        if reviews.exists():
            average = sum(review.rating for review in reviews) / reviews.count()
            return round(average, 1)
        return 0
    
    def average_rating_percentage(self):
        return self.average_rating() * 20 
        
    def total_ratings(self):
        return self.reviews.count()    

class Variant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    color = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, blank=True)
    is_listed = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True) 
    
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.product.name}-{self.color}")
        super().save(*args, **kwargs)
    
    def total_stock(self):
        result = self.sizes.aggregate(total_stock=Sum('stock'))
        return result.get('total_stock', 0) 
        
    class Meta:
            verbose_name = 'Variant'
            verbose_name_plural = 'Variants'

    def __str__(self):
        return f"{self.product.name} - {self.color}"

class VariantSize(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE,related_name='sizes' )
    size = models.CharField(max_length=50)
    stock = models.PositiveIntegerField() # stock per size
    slug = models.SlugField(unique=True, blank=True)
   

    def save(self,*args,**kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.variant.product.name}-{self.size}-{self.variant.color}")
        super().save(*args, **kwargs)    

    def __str__(self):
        return f'{self.variant.product.name}-{self.variant.color}-{self.size}'

class VariantImages(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE,related_name='images')
    image = models.ImageField(upload_to='product_variants/')

    class Meta :
          verbose_name = 'image'
          verbose_name_plural = 'images'
   
   
class Review(models.Model):

    RATING_CHOICES = [(i, i) for i in range(1, 6)]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    comments = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'

    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.rating}"  
      


