from django.shortcuts import render,redirect,get_object_or_404
from . models import Coupon
from . forms import CouponForm
from django.utils.timezone import now
from django.contrib import messages
from django.utils import timezone

# Create your views here.


def coupons(request):
    coupons = Coupon.objects.all()
    context ={
        'coupons':coupons,
        'form':CouponForm()
    }
    return render(request, 'admin_panel/coupons.html', context)


def create_coupon(request):
    if request.method == "POST":
        form = CouponForm(request.POST)
        if form.is_valid():
            coupon = form.save(commit=False)
            if coupon.expiry_at <= timezone.now():
                messages.error(request, "Expairy date must be in the future.")
            else:
                coupon.is_active=True
                coupon.save()
                messages.success(request, f"Coupon {coupon.name} created successfully!")
                return redirect('admin_coupons')

        else:
            messages.error(request, "Error creating coupon. Please check the form") 

    else:
        form = CouponForm()               
    context ={
        'coupons':coupons,
        'form':form,

    }
    return render(request, "admin_panel/coupons.html", context)


def remove_coupon(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    coupon_name = coupon.name
    coupon.delete()
    messages.success(request,f"Coupon {coupon_name} has been removed")
    return redirect('admin_coupons')