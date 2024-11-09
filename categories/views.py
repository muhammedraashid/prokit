from django.shortcuts import render,redirect,get_object_or_404
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
        name = request.POST.get("name")
        if Category.objects.filter(name=name).exclude(id=category_id).exists():
            return render(request, 'admin_panel/categories.html',{'category':category})
        else:
            category.name = name
            category.save()
            return redirect('admin_categories')
    return render(request, 'admin_panel/categories.html',{'category':category})

def category_add(request):
    if request.method == "POST":
        name = request.POST.get("name")
        
        if not name:
            return render(request, 'admin_panel/category_create.html', { 'error': 'Name cannot be empty.'}) 
        
        if Category.objects.filter(name=name).exists():
            return render(request, 'admin_panel/category_create.html', {'error': 'Category name already exists.'})
        
        Category.objects.create(name=name)
        return redirect('admin_categories')
    return render(request, 'admin_panel/categories.html')
