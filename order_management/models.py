from django.db import models
from django.contrib.auth.models import User
from address.models import Address
from coupon.models import Coupon
from cart.models import Cart
from products.models import Product,Variant,VariantSize
import random
from django.utils import timezone

# Create your models here.


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'), 
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('return_requested', 'Requested To Return') ,
        ('returned', 'Returned')
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('wallet', 'Wallet'),
        ('cod', 'Cash on Delivery'),
        ('upi', 'Online Payment (RazorPay)'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('success','Success'),
        ('pending','Pending'),
        ('refunded','Refunded'),
        ('failed','Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_status = models.CharField(max_length=100,choices=STATUS_CHOICES, default='pending')
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True,related_name='orders')
    # coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True,related_name='orders' )
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='order')
    sub_total = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_method = models.CharField(max_length=100, choices=PAYMENT_METHOD_CHOICES, default='cod')
    order_number = models.CharField(max_length=100, unique=True, null=True, blank=True)
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    payment_status = models.CharField(max_length=100, choices=PAYMENT_STATUS_CHOICES, default='pending' )
    razorpay_order_id =  models.CharField(max_length=255, null=True, blank=True)
    applied_coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE ,null=True, blank=True )
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,null=True)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_seen = models.BooleanField(default=False)
   

    def save(self,*args,**kwargs):
        if not self.order_number:
            self.order_number = self.get_order_number()
        super().save(*args,**kwargs)    

    def get_order_number(self):
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S') # date and time in string format
        random_number = random.randint(1000, 9999)   # add random numbers
        return f"ORD{timestamp}{random_number}"

    def __str__(self):
        return f"order #{self.id} by {self.user.username}"
    

class OrderItems(models.Model):

    STATUS_CHOICES = [
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('return_requested', 'Requested To Return') ,
        ('returned', 'Returned')
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True,related_name='product_order_items')
    variant = models.ForeignKey(VariantSize, on_delete=models.SET_NULL, null=True, blank=True,related_name='variant_order_items')
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sub_total = models.DecimalField(max_digits=10,decimal_places=2)
    item_status = models.CharField(max_length=100,choices=STATUS_CHOICES, default='pending')
    

    def __str__(self):
        return f"{self.quantity} x {self.product.name} - variant: {self.variant.variant.color} - {self.variant.size} in order # {self.order.id}"

  
class DeliveryCharge(models.Model):
    value = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)

    def __str__(self):
        return  self.value