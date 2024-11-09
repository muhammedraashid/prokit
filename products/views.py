
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist,ValidationError
from products.models import Product,Variant,VariantImages
from categories.models import Category
from django.db import transaction
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count

@require_http_methods(["GET", "POST"])
def add_product(request):
   
    # Define category-specific size options
    size_options = {
        "Boots": ["38", "39", "40", "41", "42", "43", "44", "45"],
        "Shorts": ["XS", "S", "M", "L", "XL"],
        "Balls": ["Size 3", "Size 4", "Size 5"],
        "Jersey": ["XS", "S", "M", "L", "XL"],
        "Socks": ["S", "M", "L"],
    }

    # Handle GET request
    if request.method == 'GET':
        categories = Category.objects.all()
        category_id = request.GET.get("category", "1")
        
        # Get selected category and its name
        selected_category = get_object_or_404(Category, id=category_id)
        category_name = selected_category.name

        # Get size options for selected category
        sizes = size_options.get(category_name, ['unavailable'])
        
        context = {
            "sizes": sizes,
            "categories": categories,
            "category_id": category_id
        }
        return render(request, 'admin_panel/add_product.html', context)

    # Handle POST request
    try:
        with transaction.atomic():
            # Extract basic product information
            category_id = request.POST.get('categoryId')
            
            # Validate category
            if not category_id:
                raise ValidationError("Category is required")
            
            # Create product
            product = Product.objects.create(
                name=request.POST.get('name'),
                price=request.POST.get('price'),
                description=request.POST.get('description', ''),
                category_id=category_id,
                brand = request.POST.get('brand',''),
                offer=request.POST.get('offer') or None,
                is_listed=request.POST.get('is_listed') == 'on'
            )

            # handle the  first variant   
            size = request.POST.get('size')
            color = request.POST.get('color')
            stock = request.POST.get('stock')

            # Create a single variant
            variant = Variant.objects.create(
                product=product,
                size=size,
                color=color,
                stock=stock
            )

            # Process images for this variant
            variant_images = []
            required_images_count = 3  # Minimum required images

            # Handle images (both required and optional)
            for j in range(1, 6):
                image_key = f'image{j}[]'
                if image_key in request.FILES:
                    images = request.FILES.getlist(image_key)
                    for image in images:
                        variant_images.append(
                            VariantImages(variant=variant, image=image)
                        )

            # Validate image count
            if len(variant_images) < required_images_count:
                raise ValidationError(
                    f"The variant ({size}-{color}) requires at least {required_images_count} images"
                )

            # Bulk create variant images
            VariantImages.objects.bulk_create(variant_images)

            messages.success(request, "Product and variant created successfully!")
            return redirect('admin_products')


    except ValidationError as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        # In production, you might want to log the full error
        
    # If there's an error, re-render the form with the current category
    categories = Category.objects.all()
    selected_category = get_object_or_404(Category, id=category_id)
    sizes = size_options.get(selected_category.name, ['unavailable'])
    
    context = {
        'categories': categories,
        'category_id': category_id,
        'sizes': sizes,
    }
    return render(request, 'admin_panel/add_product.html', context)


def update_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    category_id = product.category.id

    if request.method == "POST":
        # Get the new name from the form and strip whitespace
        name = request.POST.get("name", "").strip()
        
        # Check if name is empty after stripping spaces
        if not name:
            messages.error(request, "Product name cannot be empty or contain only spaces.")
            return render(request, 'admin_panel/product_details.html', {'product': product})

        # Check if a product with the same name already exists (excluding the current product)
        if Product.objects.filter(name=name).exclude(id=product_id).exists():
            messages.error(request, "A product with this name already exists.")
            return render(request, 'admin_panel/product_details.html', {'product': product})

        # Update product fields if validations pass
        product.name = name
        product.price = request.POST.get("price")
        product.description = request.POST.get("description")
        product.brand = request.POST.get("brand")
        product.offer = request.POST.get("offer")
        product.is_listed = request.POST.get("is_listed") == 'on'
        product.category_id = category_id

        product.save() #product saved
        messages.success(request, "Product updated successfully.")
        return redirect('admin_product_view',product_id=product.id)

    return render(request, 'admin_panel/product_details.html', {'product': product})

def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == "POST":
        product.delete()
        return redirect('admin_products')
    return render(request, 'admin_panel/products.html')


def Shop(request):
    products = Product.objects.filter(is_listed = True)
    categories = Category.objects.filter(is_listed=True)
    size_options = {
        "Boots": ["38", "39", "40", "41", "42", "43", "44", "45"],
        "Shorts": ["XS", "S", "M", "L", "XL"],
        "Balls": ["Size 3", "Size 4", "Size 5"],
        "Jersey": ["XS", "S", "M", "L", "XL"],
        "Socks": ["S", "M", "L"],
    }
    category_name = 'Jersey'  #defaultly set
    sizes = size_options.get(category_name, ['unavailable'])
    # Define color options
   
    context = {
        'products': products,
        'categories': categories,
        'sizes' : sizes,
    }
    return render(request, 'shop.html', context)



def userProductView(request,variant_id):
    variant = get_object_or_404(Variant, id=variant_id)
    product = variant.product
    category = product.category
    images = variant.images.all()
    # reviews = product.reviews.all()
    size_options = {
        "Boots": ["38", "39", "40", "41", "42", "43", "44", "45"],
        "Shorts": ["XS", "S", "M", "L", "XL"],
        "Balls": ["Size 3", "Size 4", "Size 5"],
        "Jersey": ["XS", "S", "M", "L", "XL"],
        "Socks": ["S", "M", "L"],
    }
    sizes = size_options.get(category.name, ['unavailable'])

    products = Product.objects.filter(is_listed = True)
    related_products = Product.objects.filter(Q(category = category) & Q(is_listed=True)).exclude(id=product.id)[:4]
    context = {
        'product':product,
        'category':category,
        'variant' : variant,
        'images' : images,
        'sizes' : sizes,
        'products': products,
        'related_products':related_products,
        # 'reviews':reviews
    }
    return render(request, 'product.html', context)

def adminProductView(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    variants = product.variants.prefetch_related('images').all()

    context = {
        'product': product,
        'variants': variants,
    }
    return render(request, 'admin_panel/product_details.html', context)

def list_unlist_product(request,product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == "POST":
        product.is_listed = not product.is_listed
        product.save()
    return redirect('admin_products')

def del_product(request,product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.delete()
    return redirect('admin_products')



def update_variant(request, variant_id):

    variant = get_object_or_404(Variant, id=variant_id)
    category_name = variant.product.category.name
    size_options = {
        "Boots": ["38", "39", "40", "41", "42", "43", "44", "45"],
        "Shorts": ["XS", "S", "M", "L", "XL"],
        "Balls": ["Size 3", "Size 4", "Size 5"],
        "Jersey": ["XS", "S", "M", "L", "XL"],
        "Socks": ["S", "M", "L"],
    }
    sizes = size_options.get(category_name,['unavailable'])
    if request.method == 'POST':
        # Update variant fields
        variant.size = request.POST.get('size')
        variant.color = request.POST.get('color')
        variant.stock = request.POST.get('stock')
        variant.save()

       
    
    context = {
        'variant':variant,
        'sizes': sizes
    }
    return render(request, 'admin_panel/edit_variant.html',context)



def add_variant(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    category_name = product.category.name
    size_options = {
        "Boots": ["38", "39", "40", "41", "42", "43", "44", "45"],
        "Shorts": ["XS", "S", "M", "L", "XL"],
        "Balls": ["Size 3", "Size 4", "Size 5"],
        "Jersey": ["XS", "S", "M", "L", "XL"],
        "Socks": ["S", "M", "L"],
    }
    sizes = size_options.get(category_name,['unavailable'])
    if request.method == "POST":
        size = request.POST.get('size')
        color = request.POST.get('color')
        stock = request.POST.get('stock')

        
       
        variant = Variant.objects.create(
            product=product,
            size=size,
            color=color,
            stock=stock
        )

        
        variant_images = []

        # optional images
        for j in range(1, 6):
            images = request.FILES.getlist(f'image{j}[]')
            for image in images:
                variant_images.append(
                    VariantImages(variant=variant, image=image)
                )

        # Bulk create variant images
        if variant_images:
            VariantImages.objects.bulk_create(variant_images)

        messages.success(request, "Variant created successfully!")
        return redirect('admin_product_view', product_id=product.id)

                    
    context = {
        'product':product,
        'sizes':sizes
        
    }    

    return render(request, 'admin_panel/add_variant.html', context)


def delete_variant(request,variant_id):
    variant = get_object_or_404(Variant, id=variant_id)
    if request.method == "POST":
        variant.delete()
    return redirect('admin_product_view',product_id=variant.product.id)
