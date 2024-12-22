
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist,ValidationError
from order_management.models import Order,OrderItems,DeliveryCharge
from cart.models import Cart,CartItems
from coupon.models import Coupon
from address.models import Address
from wallet.models import Wallet,WalletTransaction
from django.db import transaction
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count,Sum,F
import razorpay
from razorpay.errors import SignatureVerificationError
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json
import requests
import phonenumbers
from phonenumbers import geocoder
from decimal import Decimal
from django.utils.timezone import now, datetime, timedelta
import csv
from reportlab.lib.pagesizes import letter
import openpyxl 
from django.http import HttpResponse
from reportlab.pdfgen import canvas
import io
from django.template.loader import get_template
from xhtml2pdf import pisa

# Create your views here.

@login_required
def admin_order_management(request):
    orders = Order.objects.all().order_by('-created_at')  
    delivery_charge = DeliveryCharge.objects.get(id=1)
    delivery_charge = delivery_charge.value

    if request.method == "POST":
        filterby = request.POST.get('filterby')

        if filterby:
            if filterby != 'all':
                orders = Order.objects.filter(order_status=filterby).order_by('-created_at')
           
    context = {
        'orders': orders,
        'status_choices': Order.STATUS_CHOICES,
        'filterby': request.POST.get('filterby'),
        'value':delivery_charge
    }
    return render(request, 'admin_panel/orders.html', context)




def get_location(pincode):
    api_key = '73515090-a344-11ef-a6ab-69a0d479c7d0'
    url = 'https://app.zipcodebase.com/api/v1/search'
    params = {'codes': pincode}
    headers = {'apikey': api_key}

    try:    
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()

            if 'results' in data and pincode in data['results']:
                location = data['results'][pincode][0]
                country = location.get('country_code', None)
                state = location.get('state', None)
                city = location.get('city', None)

                return country, state, city
        return None, None, None

    except requests.exceptions.RequestException as e:
        return None, None, None

@login_required
def checkout(request):
    if request.method == "POST":
        address_type = request.POST.get('address_type')
        name = request.POST.get('name')
        street_address = request.POST.get('street_address')
        pincode = request.POST.get('pincode')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        is_default = request.POST.get('is_default') == 'on' 

        if not (address_type and name and street_address and pincode and phone and email):
            messages.error(request, "All fields are Required")
            return redirect('checkout')
        
        
        country, state, city = get_location(pincode)

        if is_default:
            Address.objects.filter(user=request.user).update(is_default=False) 

            Address.objects.create(
                user = request.user,
                address_type = address_type,
                name = name,
                country = country,
                state = state,
                city = city,
                street_address = street_address,
                pincode = pincode,
                phone = phone,
                email = email,
                is_default = is_default
            )
            messages.success(request, f"Address {address_type} added succesfully")
            return redirect('checkout')

  
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        messages.error(request,"Cart does not exist")
        redirect('home')
    
    cart_items = CartItems.objects.filter(cart=cart)
    address = Address.objects.filter(user=request.user)

    delivery_charge = DeliveryCharge.objects.get(id=1)
    delivery_charge = delivery_charge.value
    applied_coupon = None 
    discount_amount = 0 
    sub_total =  cart.calculate_total()
    total_price = sub_total + delivery_charge
    if cart.applied_coupon:
        applied_coupon =  cart.applied_coupon
        discount_amount = cart.discount_amount 
        total_price = sub_total - discount_amount 
        total_price += delivery_charge    

    coupons = Coupon.objects.filter(is_active=True, expiry_at__gt=now())    
    context = {
        'cart_items': cart_items,
        'cart': cart,
        'address': address,
        'delivery_charge':delivery_charge,
        'total_price': total_price,
        'sub_total': sub_total,
        'discount_amount':discount_amount,
        'applied_coupon':applied_coupon,
        'coupons':coupons,
        'payment_choices' : Order.PAYMENT_METHOD_CHOICES ,
          
    }

    return render(request, 'checkout.html',context)


razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

@login_required
def place_order(request):
    if request.method == "POST":
        address_id = request.POST.get('address')
        if not address_id:
            messages.error(request, "Please add an address!")
            return redirect('checkout')
        
        address = get_object_or_404(Address, id=address_id)
        payment_method = request.POST.get('payment_method')
        # coupon = request.POST.get('coupon')
        

        user = request.user
        cart = Cart.objects.get(user=user)
        cart_items = cart.cartitems.all()

        if not cart_items:
            messages.error(request, 'Your cart is empty!')
            return redirect('checkout')
        
        delivery_charge = DeliveryCharge.objects.get(id=1)
        delivery_charge = delivery_charge.value
        total_amount = cart.calculate_total() + delivery_charge
        if cart.applied_coupon:
            total_amount = total_amount - cart.discount_amount 
   
        total_amount_in_paise = int(total_amount * 100)
        
        address = get_object_or_404(Address, id=address_id)

        if payment_method == 'upi':
            request.session['address_id']= address.id

            razorpay_order = razorpay_client.order.create({
                'amount':total_amount_in_paise,
                'currency':'INR',
                'payment_capture':'1'
            })
            context = {
                'razorpay_order_id': razorpay_order['id'],
                'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                'amount': total_amount,
                'selected_address': address,  
            }
            return render(request, 'razorpay_payment.html', context)
       
        if payment_method in ['cod', 'wallet']:
            if payment_method == 'wallet':
                if total_amount > user.wallet.balance:
                    messages.error(request, "Your wallet balance is insufficient to place this order.")
                    return redirect('checkout')
                
            if payment_method == 'cod':
                if total_amount > 1000 :
                    messages.error(request, ' Cash on Delivery (COD) is only available for purchases up to ₹1000')
                    return redirect('checkout')
                
            applied_coupon = None
            dicount_amount = 0
            sub_total = cart.calculate_total()
            total_amount = sub_total + delivery_charge
            if cart.applied_coupon:
                applied_coupon = cart.applied_coupon
                dicount_amount = cart.discount_amount
                total_amount = sub_total - dicount_amount
                total_amount += delivery_charge
    
            order = Order.objects.create(
                user=user,
                address=address,    
                cart=cart,
                # coupon=coupon if coupon else None,
                sub_total = sub_total,
                total_amount= total_amount,
                payment_method = payment_method,
                applied_coupon = applied_coupon,
                discount_amount = dicount_amount,
                delivery_charge = delivery_charge
            )
            
           
            for cart_item in cart_items:
                OrderItems.objects.create(
                    order=order,
                    product=cart_item.variant_size.variant.product,
                    variant=cart_item.variant_size,
                    quantity=cart_item.quantity,
                    price=cart_item.variant_size.variant.product.price,
                    sub_total=cart_item.total_price()
                    
                )

                # Reduce stock after successful order
                variant_size = cart_item.variant_size
                if variant_size.stock >= cart_item.quantity:
                    variant_size.stock -= cart_item.quantity
                    variant_size.save()   
                
            debited_amount = Decimal(order.total_amount)

            if payment_method == "wallet":
                wallet = request.user.wallet
                wallet.balance -= debited_amount
                wallet.save()

                WalletTransaction.objects.create(
                    wallet=wallet,
                    amount=debited_amount,
                    transaction_type='debit'
                )
                messages.success(request,f"{debited_amount} debited from your wallet for payment")
                order.payment_status='success'
                order.save()
            if order:
                cart.applied_coupon = None
                cart.discount_amount = 0
                cart.cartitems.all().delete()
                cart.save()
                messages.success(request, "Order placed successfully")  
            else:
                messages.error(request,"Error occured while making an order. Please try again")   
                redirect('checkout')   
           
    
    return render(request, 'order_placed.html',{"order_number":order.order_number})

@login_required
def verify_payment(request):
    if request.method == "POST":
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('order_id')
        razorpay_signature = request.POST.get('razorpay_signature')
        address_id = request.POST.get('address_id')
        amount = request.POST.get('amount')
        
        
        user = request.user
        address = get_object_or_404(Address, id=address_id)
        payment_status = 'success'
        # verify payment using razorpay's signature verification
        try:
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id':razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            razorpay_client.utility.verify_payment_signature(params_dict)

       
        except razorpay.errors.SignatureVerificationError:
            messages.error(request, "Payment verification failed. Please try again.")
            payment_status = 'pending'

        except KeyError as e:
            messages.error(request, f"Missing parameter: {str(e)}. Please try again.")
            payment_status = 'pending'

        except ValueError as e:
            messages.error(request, f"Invalid data: {str(e)}. Please try again.")
            payment_status = 'pending'

        except razorpay.errors.BadRequestError as e:
            messages.error(request, "Invalid request to Razorpay. Please contact support.")
            payment_status = 'pending'

        except razorpay.errors.ServerError:
            messages.error(request, "Razorpay server error. Please try again later.")
            payment_status = 'pending'

        except razorpay.errors.GatewayError:
            messages.error(request, "Payment gateway error. Please try again later.")
            payment_status = 'pending'

        except razorpay.errors.ConnectionError:
            messages.error(request, "Connection issue. Please check your internet and try again.")
            payment_status = 'pending'

        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")
            payment_status = 'pending'
                    # return redirect('checkout')
        
      
        try:
            order = Order.objects.get(razorpay_order_id=razorpay_order_id, user=user)
          
            if order.payment_status == 'success':
                messages.info(request,"This order has already been paid.") 
            else:
                order.payment_status=payment_status
                order.save()
                if payment_status == 'success':
                    messages.success(request,'Payment successful')
                else:
                    messages.error(request,'Payment verification failed')    

                
                return redirect('user_order_view',ord_id = order.id) 

        except Order.DoesNotExist:
            order = None

        # payment verified successfully
        cart = Cart.objects.get(user=user)
        cart_items = cart.cartitems.all()

        if not cart_items:
            messages.error(request, 'Your cart is empty!')
            return redirect('checkout')

        # create the order now
        
        delivery_charge = DeliveryCharge.objects.get(id=1)
        delivery_charge = delivery_charge.value
        applied_coupon = None
        dicount_amount = 0
        sub_total = cart.calculate_total()
        if cart.applied_coupon:
            applied_coupon = cart.applied_coupon
            dicount_amount = cart.discount_amount
          

        order = Order.objects.create(
            user=user,
            address=address,
            cart=cart,
            total_amount=amount,
            payment_method='upi',
            # coupon=applied_coupon if applied_coupon else None,
            sub_total = sub_total,
            applied_coupon = applied_coupon,
            discount_amount = dicount_amount,
            delivery_charge = delivery_charge,
            payment_status = payment_status,
            razorpay_order_id = razorpay_order_id
        )
 
       
        for cart_item in cart_items:
            OrderItems.objects.create(
                order=order,
                product=cart_item.variant_size.variant.product,
                variant=cart_item.variant_size,
                quantity=cart_item.quantity,
                price=cart_item.variant_size.variant.product.price,
                sub_total=cart_item.total_price()
            )
            
            variant_size = cart_item.variant_size
            if variant_size.stock >= cart_item.quantity:
                variant_size.stock -= cart_item.quantity
                variant_size.save()


        cart.applied_coupon = None
        cart.discount_amount = 0
        cart.cartitems.all().delete()
        cart.save()

        messages.success(request, "Order placed successfully!")
        
        if payment_status == 'success': 
           return redirect('order_success', order_number=order.order_number)
        else: 
           return redirect('payment_failed', order_number=order.order_number)

    return redirect('checkout')


@login_required
def payment_failed(request, order_number):
   
    order = get_object_or_404(Order, order_number=order_number, user=request.user)

    context = {
        'order': order,
        'order_items': order.order_items.all(),
        'order_number':order.order_number
    }
    return render(request, 'payment_failed.html', context)  

@login_required
def order_success(request, order_number):
    
    order = get_object_or_404(Order, order_number=order_number, user=request.user)

    context = {
        'order': order,
        'order_items': order.order_items.all(),
        'order_number':order.order_number
    }
    return render(request, 'order_placed.html', context)  


def user_orders(request):
    user = request.user
    orders = user.orders.all().order_by('-created_at')
    order_items = orders.all()

    context = {
        'order_items':order_items,
        'orders':orders
    }
      
    return render(request, 'user_orders.html',context)


def cancel_order(request,ord_id):
    order = get_object_or_404(Order, id=ord_id)
    for order_item in order.order_items.all():
        variant_size = order_item.variant
        variant_size.stock += order_item.quantity
        variant_size.save()

    order.order_status = 'cancelled'
    order.save()
   
    if order.payment_method == 'upi' or order.payment_method=='wallet':
        wallet = request.user.wallet
        refund_amount = Decimal(order.total_amount)
        wallet.balance += refund_amount
        wallet.save()
        
        WalletTransaction.objects.create(
            wallet = wallet,
            amount = refund_amount,
            transaction_type = 'credit',

        )
        messages.success(request, f"₹{refund_amount} has been refunded to  wallet!")

    messages.success(request, f"Order {order.order_number} is cancelled ")
    if order.applied_coupon:
        order.applied_coupon.used_limit += 1
        order.applied_coupon.save()
        
    if request.user.is_staff:
        return redirect('admin_orders')
    else:
        return redirect('user_orders')


def cancel_order_item(request, item_id):
   
    order_item = get_object_or_404(OrderItems, id=item_id)
    order = order_item.order

    # update the returned product's stock
    variant_size = order_item.variant
    variant_size.stock += order_item.quantity
    variant_size.save()

    # update the order item status
    order_item.item_status = 'cancelled'
    order_item.save()

    refund_amount = Decimal(order_item.sub_total)
    

    if order.applied_coupon:
        # calculate total order price excluding the canceled item
        total_order_price = (
            Decimal(order.total_amount) +
            Decimal(order.discount_amount) -
            Decimal(order.delivery_charge) -
            Decimal(order_item.sub_total)
        )

        # check if the updated total still qualifies for the coupon
        if total_order_price >= order.applied_coupon.min_amount:
            # calculate the new discount for the remaining items
            new_discount_amount = (
                Decimal(total_order_price) *
                Decimal(order.applied_coupon.discount_value) / 100
            )
            new_discount_amount = min(new_discount_amount, order.applied_coupon.max_discount)

            discount_difference = Decimal(order.discount_amount) - new_discount_amount
            refund_amount = Decimal(order_item.sub_total) - discount_difference

         
            order.discount_amount = new_discount_amount
            order.total_amount = total_order_price - new_discount_amount + order.delivery_charge
            order.save()

            # message for successful refund with a reduced discount
            messages.success(request,f"₹{refund_amount} has been successfully refunded to your wallet. A discount adjustment of ₹{discount_difference} was applied." )
        else:
            # if coupon becomes invalid,

            refund_amount = Decimal(order_item.sub_total) - order.discount_amount

            total_order_price = (
                Decimal(order.total_amount) +
                Decimal(order.discount_amount) -
                Decimal(order_item.sub_total)
            )
            messages.success(request, f"₹{refund_amount} has been successfully refunded to your wallet. A discount adjustment of ₹{order.discount_amount} was applied.")

            # reset the coupon
            order.applied_coupon.used_count -= 1
            order.applied_coupon.used_limit += 1
            order.applied_coupon = None
            order.discount_amount = Decimal(0)
            order.total_amount = total_order_price 
            order.save()
            
            # inform the user about the coupon invalidation
            messages.info(request,"The coupon was invalidated as the total amount after cancellation fell below the minimum required.")
    else:
        # refund full item subtotal if no coupon is applied
        
        refund_amount = Decimal(order_item.sub_total)

    if order.payment_method in ['upi', 'wallet']:
        # rrocess wallet refund
        wallet = order.user.wallet
        wallet.balance += refund_amount
        wallet.save()
        
        if order.order_items.all().exclude(item_status__in=['cancelled', 'returned']).count() == 0:
            refund_amount += order.delivery_charge

    
        WalletTransaction.objects.create(
            wallet=wallet,
            amount=refund_amount,
            transaction_type='credit',
        )

        # Final success message for wallet refund
        messages.success(
            request,
            f"₹{refund_amount} has been successfully refunded to your wallet."
        )
        
    if order.order_items.all().exclude(item_status__in=['cancelled', 'returned']).count() == 0:
        order.order_status = 'cancelled'
        order.discount_amount = 0 
        order.delivery_charge  = 0
        order.total_amount = 0
        order.save()          
    
    messages.success(request, f"Order Item {order_item.product.name} is cancelled ")
    return redirect('user_order_view',ord_id=order.id)
  

       

# ---------------------------------------------------    
    # if  order.applied_coupon:
    #     total_order_price = Decimal(order.total_amount) + Decimal(order.discount_amount) # total price without coupon discounts
    #     total_order_price -= Decimal(order_item.sub_total) # total price without coupon discount after removing
    #     discount_amount = (Decimal(total_order_price) * Decimal(order.applied_coupon.discount_value) / 100)   # calculate discount amount after item cancelled
    #     order.discount_amount = Decimal(order.applied_coupon.max_discount) if Decimal(order.applied_coupon.max_discount) > Decimal(discount_amount) else Decimal(discount_amount)
    #     order.total_amount = Decimal(total_order_price) - Decimal(order.discount_amount) # total amount with discount
    #     order.total_amount +=  Decimal(order.delivery_charge) # total amount after applying delivery charge
    #     order.save()

    #     if all(order_item.item_status == 'cancelled' for order_item in order.order_items.all()):
    #         order.delivery_charge = 0.00
    #         order.order_status = 'cancelled'
    #         order.save()
            
    #     if order.total_amount < order.applied_coupon.min_amount:
    #         if order.payment_method == 'upi' or order.payment_method=='wallet':
    #             wallet = order.user.wallet
    #             discount = Decimal(0) if Decimal(order.applied_coupon.max_discount) > Decimal(discount_amount) else (order_item.sub_total * Decimal(order.applied_coupon.discount_value)) / Decimal(100)
    #             refund_amount = Decimal(order_item.sub_total) - discount

    #             wallet.balance += refund_amount
    #             wallet.save()
                
            
    #             WalletTransaction.objects.create(
    #                 wallet = wallet,
    #                 amount = refund_amount,
    #                 transaction_type = 'credit',

    #             )
    #             messages.success(request, f"₹{refund_amount} has been successfully refunded to your wallet. A discount of ₹{discount} was deducted due to the applied coupon.")

    #         order.applied_coupon.used_count -= 1
    #         order.applied_coupon.used_limit +=1
    #         order.applied_coupon = None
    #         order.discount_amount = 0.00
    #         order.save()
    #         messages.info(request, "Coupon invalid: Total amount is less than the minimum required.")    
    # else:    
    #     all_cancelled_or_returned = all(
    #     item.item_status in ["returned", "cancelled"] for item in order.order_items.all()
    #     )

    #     for order_item in order.order_items.all():
    #         if all_cancelled_or_returned:
    #             order.total_amount -= sum(Decimal(item.sub_total) for item in order.order_items.all())
    #             order.delivery_charge = 0.00
    #         else:
    #             order.total_amount -= Decimal(order_item.sub_total)

        
    #     order.total_amount = max(order.total_amount, Decimal(0)) # ensure total is positive value
    #     order.save()


    # if order.order_items.all().exclude(item_status__in=['cancelled', 'returned']).count() == 0:
    #        order.order_status = 'cancelled'
    #        order.discount_amount = 0 
    #        order.save()          
    
    # if order.payment_method == 'upi' or order.payment_method=='wallet':
    #     wallet = order.user.wallet
    #     refund_amount = Decimal(order_item.sub_total)

    #     wallet.balance += refund_amount
    #     wallet.save()
        
    #     WalletTransaction.objects.create(
    #         wallet = wallet,
    #         amount = refund_amount,
    #         transaction_type = 'credit',

    #     )
    #     messages.success(request, f"₹{refund_amount} has been refunded to  wallet!")
        

    # messages.success(request, f"Order Item {order_item.product.name} is cancelled ")
    # return redirect('user_order_view',ord_id=order.id)

def return_order(request,ord_id):
    order = get_object_or_404(Order, id=ord_id)
    for order_item in order.order_items.all():
        variant_size = order_item.variant
        variant_size.stock += order_item.quantity
        variant_size.save()
    
    if request.user.is_staff:   
        
        order.order_status = 'returned'
        order.save()
        wallet = order.user.wallet
        refund_amount = Decimal(order.total_amount)
        wallet.balance += refund_amount
        wallet.save()
        order.payment_status = 'Refunded'
        order.save()

        WalletTransaction.objects.create(
            wallet = wallet,
            amount = refund_amount,
            transaction_type = 'credit',

        )
        messages.success(request, f"₹{refund_amount} has been refunded to  wallet!")

        messages.success(request, f"Order {order.order_number} is Retruned")
        return redirect('admin_orders')
        
    else:
        order.order_status = 'return_requested'
        order.save()
        return redirect('user_orders')
    
    # return redirect('admin_orders')
def return_order_item(request, item_id):
    order_item = get_object_or_404(OrderItems, id=item_id)
    order = order_item.order
    #updating the retuned product stock
    variant_size =  order_item.variant
    variant_size.stock += order_item.quantity
    variant_size.save()
    if request.user.is_staff:
  
        order_item.item_status = 'returned'
        order_item.save()
        
        if  order.applied_coupon:
            total_order_price = Decimal(order.total_amount) + Decimal(order.discount_amount) # total price without coupon discounts
            total_order_price -= Decimal(order_item.sub_total) + Decimal(order.delivery_charge) # total price without coupon discount after removing
            order.discount_amount = (total_order_price * order.applied_coupon.discount_value) / 100  # calculate discount amount after item returned
            order.total_amount = Decimal(total_order_price) - Decimal(order.discount_amount) # total amount with discount
            order.total_amount +=  Decimal(order.delivery_charge) # total amount after applying delivery charge
            order.save()

                
            if order.total_amount < order.applied_coupon.min_amount:
                order.applied_coupon.used_count -= 1
                order.applied_coupon.used_limit +=1
                order.applied_coupon = None
                order.discount_amount = 0.00
                order.save()
                messages.info(request, "Coupon invalid: Total amount is less than the minimum required.")    
        else:    
            order.total_amount -= Decimal(order_item.sub_total) 
            order.save()

        if order.order_items.all().exclude(item_status__in=['cancelled', 'returned']).count() == 0:
            order.status = 'returned'
            order.discount_amount = 0 
            order.save()

        wallet = order.user.wallet
        if order.applied_coupon:
            discount = (order_item.sub_total * order.applied_coupon.discount_value ) / 100
            refund_amount = Decimal(order_item.sub_total) - discount
        else :
            refund_amount = Decimal(order_item.sub_total)
        
        # refund the amount to the user wallet
        wallet.balance += refund_amount
        wallet.save()
        
       # update wallet transaction history
        WalletTransaction.objects.create(
            wallet = wallet,
            amount = refund_amount,
            transaction_type = 'credit',

        )
        if order.applied_coupon:
            messages.success(request, f"₹{refund_amount} has been successfully refunded to your wallet. A discount of ₹{discount} was deducted due to the applied coupon.")
        else:
             messages.success(request, f"₹{refund_amount} has been refunded to  wallet!")  

        messages.success(request, f"Order {order.order_number} is Returned")
        return redirect('admin_order_view',ord_id=order.id)      
    
    else:
        order_item.item_status = 'return_requested'
        order_item.save()
        return redirect('user_order_view',ord_id=order.id)


def order_status(request, ord_id):
    order = get_object_or_404(Order, id=ord_id)
    if request.method == 'POST':
        status = request.POST.get('order_status')
        
        order.order_status = status
        order.save()
        if order.order_status == 'returned':
            return redirect('admin_order_view',ord_id=order.id) 
        if order.order_status == 'delivered':
            order.payment_status = 'paid'
            order_items = order.order_items.filter(item_status='pending')
            for item in order_items:
                item.item_status = 'delivered'
                item.save()

        if order.order_status == 'cancelled':
            order_items = order.order_items.filter(item_status='pending')
            for item in order_items:
                item.item_status = 'cancelled'
                item.save()
        order.save()

        return redirect('admin_orders')
    return redirect('admin_orders')

def admin_order_view(request,ord_id): 
    order = get_object_or_404(Order, id=ord_id)
    context = {
        'order':order,
        'excluded_statuses' : ['cancelled', 'delivered', 'return_requested','returned']
    }
    return render(request, 'admin_panel/admin_order_details.html', context)

def user_order_view(request,ord_id):
    order = get_object_or_404(Order, id=ord_id)
    context = {
        'order':order,
    }
    return render(request, 'user_order_details.html', context)




def export_sales_report(request):
    
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    ex_format =  request.GET.get('format')


   
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    orders = Order.objects.filter(order_status='delivered')

    if start_date and end_date:
        orders = orders.filter(order_date__date__range=[start_date, end_date])
    elif start_date:
        orders = orders.filter(order_date__date__gte=start_date)
    elif end_date:
        orders = orders.filter(order_date__date__lte=end_date)
   
    if ex_format == 'csv': 
        
       if ex_format == 'csv': 
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Order ID', 'Order Number', 'Order Date', 'Total Amount', 'Status'])

        for order in orders:
            writer.writerow([order.id, order.order_number, order.order_date.strftime('%Y-%m-%d'), order.total_amount, order.get_order_status_display()])

        return response

    elif ex_format == 'excel':
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="sales_report.xlsx"'
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Sales Report"

 
        ws.append(['Order ID', 'Order Number', 'Order Date', 'Total Amount', 'Status'])

        for order in orders:
            order_date = order.order_date.replace(tzinfo=None) if order.order_date else None
            ws.append([order.id, order.order_number, order_date.strftime('%Y-%m-%d') if order_date else '', order.total_amount, order.get_order_status_display()])

        wb.save(response)
        return response
    elif ex_format == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'
        
        # Create a PDF document
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)

        # Define some starting position and style
        x = 50
        y = 750
        c.setFont("Helvetica", 10)

        # Add the header row
        c.drawString(x, y, "Order ID")
        c.drawString(x + 100, y, "Order Number")
        c.drawString(x + 200, y, "Order Date")
        c.drawString(x + 300, y, "Total Amount")
        c.drawString(x + 400, y, "Status")
        
        y -= 20

        # Add the orders to the PDF
        for order in orders:
            c.drawString(x, y, str(order.id))
            c.drawString(x + 100, y, order.order_number)
            c.drawString(x + 200, y, order.order_date.strftime('%Y-%m-%d'))
            c.drawString(x + 300, y, str(order.total_amount))
            c.drawString(x + 400, y, order.get_order_status_display())
            y -= 20

            # Add a page if needed
            if y < 50:
                c.showPage()
                y = 750

        c.showPage()
        c.save()

        # Return the response with PDF content
        buffer.seek(0)
        response.write(buffer.read())
        return response

    return HttpResponse("Invalid format", status=400)
    

def export_invoice(request, ord_id):
    order = get_object_or_404(Order, id=ord_id)
    
    context = {
        'order':order
    }
#load html template   
    template = get_template('invoice.html')
    html = template.render(context)
# cereate pdf 
    response = HttpResponse(content_type='application/pdf') 
    response['Content-Disposition'] = f'attachment; filename="Invoice_{order.order_number}.pdf"'
# genarate pdf
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>'+html+'</pre>')
    
    return response


def set_delivery_charge(request):
    if request.method == "POST":
        try:
            value = request.POST.get('value')
            value = float(value)
            if value < 0:
                messages.error(request, "Invalid Value! Delivery charge cannot be negative.")
                return redirect('admin_orders')

            dc, created = DeliveryCharge.objects.get_or_create(id=1)
            dc.value = value
            dc.save()

            messages.success(request, "Delivery Charge changed successfully.")
        except ValueError:
            messages.error(request, "Invalid input! Please enter a valid number.")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

    return redirect('admin_orders')


# def redirect_to_payment(request):
#     razorpay_order = razorpay_client.order.create({
#                 'amount':total_amount_in_paise,
#                 'currency':'INR',
#                 'payment_capture':'1'
#             })
#             context = {
#                 'razorpay_order_id': razorpay_order['id'],
#                 'razorpay_key_id': settings.RAZORPAY_KEY_ID,
#                 'amount': total_amount,
#                 'selected_address': address.id,  
#             }
#     return render(request, 'razorpay_payment.html', context)



@login_required
def retry_payment(request, ord_id):
    order = get_object_or_404(Order, id=ord_id, user=request.user)

    if order.payment_status == 'success':
        messages.info(request, "This order has already been paid.")
        return redirect('user_order_view', ord_id=ord_id)

    # clear any existing Razorpay order ID before creating a new one
    order.razorpay_order_id = None
    order.save()

    # create a new Razorpay order
    total_amount_in_paise = int(order.total_amount * 100)
    razorpay_order = razorpay_client.order.create({
        'amount': total_amount_in_paise,
        'currency': 'INR',
        'payment_capture': '1',
    })

    # assign the new Razorpay order ID
    order.razorpay_order_id = razorpay_order['id']
    order.save()

    context = {
        'razorpay_order_id': order.razorpay_order_id,  # ensure razorpay_order_id is passed to the template
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'amount': order.total_amount,
        'selected_address': order.address,
    }
    return render(request, 'razorpay_payment.html', context)


