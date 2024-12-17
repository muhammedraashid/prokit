from django.db import models
from django.contrib.auth.models import User
from products.models import VariantSize

# Create your models here.


class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wishlist')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wishlist of {self.user.username} created on {self.created_at}"
    

class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items')
    variant_size = models.ForeignKey(VariantSize, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Item: {self.product.name} in wishlist {self.wishlist.id}"
