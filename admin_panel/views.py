from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from products.models import Product
from categories.models import Category
from order_management.models import Order,OrderItems
from coupon.models import Coupon
from django.db.models import Sum
from django.db.models.functions import TruncWeek,TruncMonth,TruncYear
from django.utils import timezone
from datetime import timedelta,datetime


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

@staff_member_required
@login_required
def adminDashboard(request):
    total_users = User.objects.count()
    total_orders = Order.objects.count()
    pending_coupons = Coupon.objects.count()
    top_products = (
        OrderItems.objects.values('product__name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:10]
    )
    
    top_categories = (
        OrderItems.objects.values('product__category__name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:10]
    )
    top_brands = (
        OrderItems.objects.values('product__brand').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:10]
    )
    
    week_start = timezone.now() - timedelta(days=7)

    weekly_products = (
    OrderItems.objects.filter(order__created_at__gte = week_start)
        .values('product__name')
        .annotate(total_quantity=Sum('quantity'))
        .order_by('-total_quantity')[:10]  
    )

    weekly_categories = (
        OrderItems.objects.filter(order__created_at__gte = week_start)
        .values('product__category__name')
        .annotate(total_quantity=Sum('quantity'))
        .order_by('-total_quantity')[:5]
    )
    weekly_product_names = [item['product__name'] for item in weekly_products]
    weekly_product_quantities = [item['total_quantity'] for item in weekly_products]

    weekly_category_names = [item['product__category__name'] for item in weekly_categories]
    weekly_category_quantities = [item['total_quantity'] for item in weekly_categories]

    month_start = timezone.now() - timedelta(days=30)

    monthly_products = (
    OrderItems.objects.filter(order__created_at__gte = month_start)
        .values('product__name')
        .annotate(total_quantity=Sum('quantity'))
        .order_by('-total_quantity')[:10]  
    )

    monthly_categories = (
        OrderItems.objects.filter(order__created_at__gte = month_start)
        .values('product__category__name')
        .annotate(total_quantity=Sum('quantity'))
        .order_by('-total_quantity')[:5]
    )

    monthly_product_names = [item['product__name'] for item in monthly_products]
    monthly_product_quantities = [item['total_quantity'] for item in monthly_products]
    
    monthly_category_names = [item['product__category__name']for item in  monthly_categories]
    monthly_category_quantities = [item['total_quantity'] for item in monthly_categories]
    
    # -------------------------- sales report ----------------------------------------------------
    
    filter_type = request.GET.get('filter', 'daily')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
  
   
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    today = timezone.now()
    orders = Order.objects.filter(order_status='delivered', order_date__date = today)

    if start_date and end_date:
        orders = orders.filter(order_date__date__range=[start_date, end_date])
    elif start_date:
        orders = orders.filter(order_date__date__gte=start_date)
    elif end_date:
        orders = orders.filter(order_date__date__lte=end_date)


    if filter_type == 'daily':
       today = timezone.now().date()
       orders = Order.objects.filter(order_status='delivered', order_date__date= today)
       total_sales = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    elif filter_type == 'weekly':
        today = timezone.now().date()
        week_start = today - timedelta(days=7)
        orders = Order.objects.filter(order_status='delivered', order_date__date__range=[week_start, today])
        total_sales = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    elif filter_type == 'yearly':
        today = timezone.now().date()
        year_start = today.replace(month=1, day=1)
        orders = Order.objects.filter(order_status='delivered', order_date__date__gte=year_start)
        total_sales = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    elif filter_type == 'custom':
         if not start_date or not end_date :
             messages.error(request,"Select the Custom Range Starting and Ending dates")
             return redirect('admin_dashboard') 
         orders = Order.objects.filter(order_status='delivered', order_date__date__range=[start_date, end_date])
         total_sales = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    context = {
        'total_users': total_users,
        'total_orders': total_orders,
        'pending_coupons': pending_coupons,
        'current_page': 'dashboard',
        'top_products' : top_products,
        'top_categories' :top_categories,
        'top_brands':top_brands,
        'weekly_product_names':weekly_product_names,
        'weekly_product_quantities':weekly_product_quantities,
        'weekly_category_names':weekly_category_names,
        'weekly_category_quantities':weekly_category_quantities,
        'monthly_product_names':monthly_product_names,
        'monthly_product_quantities':monthly_product_quantities,
        'monthly_category_names':monthly_category_names,
        'monthly_category_quantities':monthly_category_quantities,
        'orders':orders,
        'total_sales':total_sales,
        'filter_type': filter_type,
        'start_date':start_date,
        'end_date': end_date,
    }

    return render(request, 'admin_panel/dash_board.html', context)

@staff_member_required
@login_required
def adminUsers(request):
    users = User.objects.exclude(id = 1).order_by('date_joined').reverse()
    context = {
        'users': users,
        'current_page': 'users',
        'placeholder': 'Search by username, email, etc.'
    }
    return render(request, 'admin_panel/users.html',context)

@staff_member_required
def user_block_unblock(request, user_id):  
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        user.is_active = not user.is_active  
        user.save()
        
        if user.is_active:
            messages.success(request, f"{user.username} has been unblocked.")
        else:
            messages.warning(request, f"{user.username} has been blocked.")
        
    return redirect('admin_users')

@staff_member_required
@login_required
def adminProducts(request):
    products = Product.objects.all()
    context = {
        'products': products,
        'current_page': 'products',
        'placeholder': 'Search by product name '
    }
    return render(request, 'admin_panel/products.html', context)
@staff_member_required
@login_required
def adminCategories(request):
    categories = Category.objects.all()
    for category in categories:
        category.sizes_text = ", ".join([size.size for size in category.sizes.all()])
    context = {
        'categories': categories,
        'current_page': 'categories',
        'placeholder': 'Search by category name'
    }
    return render(request, 'admin_panel/categories.html',context)

@staff_member_required
@login_required
def adminLogout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('admin_signin')  


