from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from products.models import Product
from categories.models import Category


# Create your views here.

def adminSignIn(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:  # Check user is an admin
            login(request, user)
            return redirect('admin_dashboard')  # Redirect to admin dashboard
        else:
            messages.error(request, 'Invalid credentials or access restricted!')

    return render(request, 'admin_panel/admin_signin.html')

@login_required
def adminDashboard(request):
    total_users = User.objects.count()
    total_orders = 75
    pending_coupons = 10 

    context = {
        'total_users': total_users,
        'total_orders': total_orders,
        'pending_coupons': pending_coupons,
        'current_page': 'dashboard',
    }

    return render(request, 'admin_panel/dash_board.html', context)

@login_required
def adminUsers(request):
    users = User.objects.exclude(id = 1).order_by('username')
    context = {
        'users': users,
        'current_page': 'users',
        'placeholder': 'Search by username, email, etc.'
    }
    return render(request, 'admin_panel/users.html',context)

def user_block_unblock(request, user_id):  # Admin block/unblock user
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        user.is_active = not user.is_active  
        user.save()
        
        if user.is_active:
            messages.success(request, f"{user.username} has been unblocked.")
        else:
            messages.warning(request, f"{user.username} has been blocked.")
        
    return redirect('admin_users')


@login_required
def adminProducts(request):
    products = Product.objects.all()
    context = {
        'products': products,
        'current_page': 'products',
        'placeholder': 'Search by product name '
    }
    return render(request, 'admin_panel/products.html', context)

@login_required
def adminCategories(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'current_page': 'categories',
        'placeholder': 'Search by category name'
    }
    return render(request, 'admin_panel/categories.html',context)


@login_required
def adminLogout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('admin_signin')  


