from django.shortcuts import render,redirect,get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Wishlist, WishlistItem
from products.models import VariantSize
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import IntegrityError


# Create your views here.

@login_required
def add_to_wishlist(request, variant_size_slug):
    try:
        variant = get_object_or_404(VariantSize, slug=variant_size_slug)
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)

        if WishlistItem.objects.filter(wishlist=wishlist, variant_size=variant).exists():
            messages.error(request, "Item already in wishlist")
            return redirect('wishlist')
        
        WishlistItem.objects.create(
            wishlist = wishlist,
            variant_size = variant

        )
        messages.success(request, 'Item added to wihlist ')
        return redirect('wishlist')
    except VariantSize.DoesNotExist:
        messages.error(request, "Product item not found !")
        return redirect('wishlist')
    except IntegrityError:
        messages.error(request, "error occured while adding this item!")
        return redirect('wishlist')
    

def wishlist(request):
    user = request.user
    wishlist = Wishlist.objects.filter(user=user).first()

    if wishlist:
        wishlist_items = wishlist.items.all()
    else:
        wishlist_items = []        
    
    context = {
        'wishlist':wishlist,
        'wishlist_items':wishlist_items,
    }
    return render(request, 'wishlist.html',context)    

def remove_from_wishlist(request, variant_size_slug):
    variant_size = get_object_or_404(VariantSize,slug=variant_size_slug)
    if request.method == "POST":
         WishlistItem.objects.filter(variant_size=variant_size).delete()
    return redirect('wishlist')