from django.shortcuts import render,redirect,get_object_or_404
from .models import Category, Size
from django.db.models import Q
from django.contrib import messages
from django.contrib import messages
from .models import Category

# Create your views here.
def category_list_unlist(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == "POST":
        category.is_listed = not category.is_listed
        category.save()

    return redirect('admin_categories')    



def category_edit(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        category_offer = request.POST.get('offer', '').strip()
        category_sizes = request.POST.get('sizes', '').strip()
 
        if category_offer == "" : 
            category_offer = 0.00
        else:
            try:
                category_offer = float(category_offer)
            except ValueError:
                messages.error(request, "Invalid entry for offer!")

        if not name:
            messages.error(request, "Category name cannot be empty.")
            return redirect('category_edit', category_id=category_id)

         
        if  category_offer >= 100 :
            messages.error(request, "Invalid entry for offer !")
            return redirect('admin_categories')
        
        if Category.objects.filter(name__iexact=name).exclude(id=category_id).exists():
            messages.error(request, f"The category name '{name}' already exists.")
            return redirect('category_edit', category_id=category_id)

       
        category.name = name
        if category_offer:
            category.offer = category_offer
        else:
            category.offer = 0.00    
        category.save()
        sizes_list = [size.strip().upper() for size in category_sizes.split(',') if size.strip()]

        current_sizes = category.sizes.all()
        for size in current_sizes:
            if size.size not in sizes_list:
                size.delete()

        for size in sizes_list:
            if not category.sizes.filter(size=size).exists(): 
                Size.objects.create(category=category, size=size)
        category.save()
        messages.success(request, f"Category '{name}' updated successfully.")
        return redirect('admin_categories')  
    return redirect('admin_categories')


def category_add(request):
    if request.method == "POST":
        category_name = request.POST.get('name', '').strip()
        category_offer = request.POST.get('offer', '').strip()
        if not category_offer:
            category_offer = 0.00
        else:
            try:
                category_offer = float(category_offer)
            except ValueError:
                messages.error(request, "Invalid entry for offer!")
            
        if not category_name:
            messages.error(request, "Category name cannot be empty.")
            return redirect('admin_categories')
        
        if category_offer >= 100 :
            messages.error(request, "Invalid entry for offer !")
            return redirect('admin_categories')

        if Category.objects.filter(name__iexact=category_name).exists():
            messages.error(request, f"The category '{category_name}' already exists.")
            return redirect('admin_categories')
        # Create the category
        category = Category.objects.create(name=category_name,offer=category_offer)

        category_sizes = request.POST.get('sizes', '').strip()
        sizes_list = [size.strip().upper() for size in category_sizes.split(',') if size.strip()]
        for size in sizes_list:
            Size.objects.create(category=category, size=size)

        messages.success(request, f"Category '{category_name}' added successfully.")
        return redirect('admin_categories') 