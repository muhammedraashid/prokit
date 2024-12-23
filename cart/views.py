from django.shortcuts import render,redirect,get_object_or_404
from .models import Cart,CartItems
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse,JsonResponse
from django.core.exceptions import ObjectDoesNotExist,ValidationError
from products.models import Product,Variant,VariantImages,VariantSize
from wishlist.models import Wishlist,WishlistItem
from categories.models import Category,Size
from django.db import transaction
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count,Sum,F
import json
from django.views.decorators.csrf import csrf_exempt 
from coupon.models import Coupon
from django.utils.timezone import now

# Create your views here.


@login_required
def CartView(request):
    user = request.user
    cart = user.cart
    cart_items = cart.cartitems.select_related('variant_size__variant__product').prefetch_related('variant_size__variant__images')
    
    # if request.method == 'POST':
    #     total_price = request.POST.get('item_total')
   
    for item in cart_items:
        item.variant = item.variant_size.variant
        item.product = item.variant.product
        item.images = item.variant.images.all()
        item.current_stock = item.variant_size.stock
        item.selected_size = item.variant_size.size
       
        # item.slug = item.variant_size.slug  
    applied_coupon = None 
    discount_amount = 0 
    sub_total = cart.calculate_total()  
    total_price = sub_total  
    if cart.applied_coupon:
        applied_coupon =  cart.applied_coupon
        discount_amount = cart.discount_amount 
        total_price = sub_total - discount_amount
       
    coupons = Coupon.objects.filter(is_active=True, expiry_at__gt=now()) 
       
    context = {
        'cart_items': cart_items,
        "total_price" : total_price ,
        "sub_total":sub_total,
        'items_count':cart.cartitems.all().count(),
        'coupons':coupons,
        'applied_coupon':applied_coupon,
        'discount_amount':discount_amount

    }
    return render(request, 'cart.html', context)



def add_to_cart(request,variant_size_slug):
    user = request.user
    variant_size = get_object_or_404(VariantSize,slug=variant_size_slug)
    cart = Cart.objects.get(user=user)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity',1))
        if quantity <= 10 : 
            cart_item, created = CartItems.objects.get_or_create(
                cart = cart,
                variant_size = variant_size,
                price_at_time =  variant_size.variant.product.price
            )
            WishlistItem.objects.filter(variant_size=variant_size).delete() # remove item from wishlist if exists
            if not created:
                if cart_item.quantity + quantity > 10:
                    cart_item.quantity += quantity
                    cart_item.save()    
                else:
                    messages.warning(request,f"This product is already in your cart!")
            if cart.applied_coupon:         
                cart.applied_coupon = None
                cart.discount_amount = 0
                cart.save()  
                messages.info(request, "Coupon removed as new items were added to your cart. Reapply the coupon if needed.")      
            messages.success(request,'Product added to cart')
        
    return redirect('cart')

@login_required
def remove_from_cart(request,item_id):
    cart = request.user.cart
    if cart.applied_coupon:
        applied_coupon = cart.applied_coupon
        applied_coupon.used_limit += 1  
        applied_coupon.save()  

        if cart.applied_coupon:         
            cart.applied_coupon = None
            cart.discount_amount = 0
            cart.save()  
            messages.info(request, "Coupon removed as an item were removed to your cart. Reapply the coupon if needed.")   

    cart_item = get_object_or_404(CartItems, id = item_id)
    cart_item.delete()
    
    return redirect('cart')


@login_required
@require_POST
def update_cart(request):
    data = json.loads(request.body)
    user = request.user
    cart = user.cart
    coupon_id = data.get('coupon_id')
    discount_amount=0
    cart_total = 0
    cart_items = cart.cartitems.all()
    try:
        cart_item = CartItems.objects.get(
            id=data['item_id'],
            cart=cart,
            variant_size__variant__id=data['variant_id']
        )
        
        # Validation for quantity constraints
        current_stock = cart_item.variant_size.stock
        requested_quantity = data['quantity']

        if requested_quantity <= 0:
            return JsonResponse({
                'status': 'error', 
                'message': 'Quantity must be at least 1',
                'current_quantity': cart_item.quantity
            })

        if requested_quantity > 10:
            return JsonResponse({
                'status': 'error', 
                'message': 'Maximum limit is 10 units',
                'current_quantity': cart_item.quantity
            })

        if requested_quantity > current_stock:
            return JsonResponse({
                'status': 'error', 
                'message': f'Only {current_stock} units available',
                'current_quantity': cart_item.quantity
            })

      
        cart_item.quantity = requested_quantity
        cart_item.save()

        cart_subtotal = sum(item.quantity * item.price_at_time for item in cart_items)

        if coupon_id:
            try:
                coupon = Coupon.objects.get(id=coupon_id)
              
            except Coupon.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid coupon selected'
                })
            
            
            subtotal = sum(item.quantity * item.price_at_time for item in cart_items)
            if subtotal < coupon.min_amount:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Coupon requires a minimum amount of ₹{coupon.min_amount}'
                })
            
            discount_amount = (subtotal * coupon.discount_value) / 100
            if discount_amount > coupon.max_discount:
                discount_amount = coupon.max_discount
            
        
            cart.applied_coupon = coupon
            cart.discount_amount = discount_amount
            cart.save()
        
            
            cart_total = cart_subtotal - subtotal

        return JsonResponse({
            'status': 'success',
            'item_total': cart_item.quantity * cart_item.price_at_time,
            'cart_subtotal': cart_subtotal,
            'current_quantity': cart_item.quantity,
            'cart_total': cart_total,
            'discount_amount':discount_amount,
        })

    except CartItems.DoesNotExist:
        return JsonResponse({
            'status': 'error', 
            'message': 'Cart item not found'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error', 
            'message': str(e)
        })

def remove_coupon(request):
    cart = request.user.cart
    cart.applied_coupon = None
    cart.discount_amount = 0
    cart.save()
    return redirect('cart')