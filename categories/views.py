from django.shortcuts import render,redirect,get_object_or_404
from .models import Category
from django.db.models import Q
from django.contrib import messages

# Create your views here.
def category_list_unlist(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == "POST":
        category.is_listed = not category.is_listed
        category.save()

    return redirect('admin_categories')    

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Category

def category_edit(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        category_offer = float(request.POST.get('offer'))
 
       
        if not name:
            messages.error(request, "Category name cannot be empty.")
            return redirect('category_edit', category_id=category_id)

         
        if 0 > category_offer >= 100 :
            messages.error(request, "Invalid entry for offer !")
            return redirect('admin_categories')

        if Category.objects.filter(name__iexact=name).exclude(id=category_id).exists():
            messages.error(request, f"The category name '{name}' already exists.")
            return redirect('category_edit', category_id=category_id)

       
        category.name = name
        if category_offer:
            category.offer = category_offer
        category.save()
        messages.success(request, f"Category '{name}' updated successfully.")
        return redirect('admin_categories')  
    return redirect('admin_categories')


def category_add(request):
    if request.method == "POST":
        category_name = request.POST.get('name', '').strip()
        category_offer = float(request.POST.get('offer',0))

        if not category_name:
            messages.error(request, "Category name cannot be empty.")
            return redirect('admin_categories')
        
        if 0 > category_offer >= 100 :
            messages.error(request, "Invalid entry for offer !")
            return redirect('admin_categories')

        if Category.objects.filter(name__iexact=category_name).exists():
            messages.error(request, f"The category '{category_name}' already exists.")
            return redirect('admin_categories')

        # Create the category
        Category.objects.create(name=category_name,offer=category_offer)
        messages.success(request, f"Category '{category_name}' added successfully.")
        return redirect('admin_categories') 