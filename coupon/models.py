from django.db import models
from django.utils import timezone

# Create your models here.
class Coupon(models.Model):
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    code = models.CharField(max_length=100, unique=True)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2 ,default=0.00)
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    used_limit = models.PositiveIntegerField(default=1)
    used_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    expiry_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Coupon"
        verbose_name_plural = "Coupons"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.code}"
    
    def is_valid(self):

        if self.expiry_at <= timezone.now():
            return False
        if self.used_count >= self.used_limit:
            return False
        return self.is_active 