from django.db import models
from django.contrib.auth.models import User
from products.models import Product,Variant,VariantSize
from django.db.models import Sum,F
from coupon.models import Coupon

# Create your models here.
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    applied_coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE ,null=True, blank=True , default=None)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def calculate_total(self):
      return self.cartitems.aggregate(total=Sum(F('quantity') * F('price_at_time')))['total'] or 0
    

    def get_total_items(self):
        
        return self.cartitems.aggregate(total=Sum('quantity'))['total_items'] or 0
        

    def __str__(self):
        return f"cart for {self.user.username}"
    

class CartItems(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cartitems")
    variant_size = models.ForeignKey(VariantSize, on_delete=models.CASCADE, related_name='cart_items') 
    quantity =  models.PositiveIntegerField(default=1)
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2)
   
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['cart', 'variant_size'], name='unique_cart_variant')
        ]

    def __str__(self):
        return f" {self.variant.product.name}(x{self.quantity})"

    def total_price(self):
        return self.quantity * self.price_at_time   

