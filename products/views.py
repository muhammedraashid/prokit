
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse,JsonResponse
from django.core.exceptions import ObjectDoesNotExist,ValidationError
from products.models import Product,Variant,VariantImages,VariantSize
from categories.models import Category,Size
from order_management.models import Order,OrderItems
from django.db import transaction
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count,Sum, Prefetch


@require_http_methods(["GET", "POST"])
def add_product(request):
   
    if request.method == 'GET':
        categories = Category.objects.all()
        category_id = request.GET.get("category", "1")

      
        selected_category = get_object_or_404(Category, id=category_id)
        category_name = selected_category.name

        sizes = Size.objects.filter(category=selected_category).values_list('size', flat=True) # it return a list of sizes

        
        context = {
            "sizes": sizes,
            "categories": categories,
            "category_id": category_id
        }
        return render(request, 'admin_panel/add_product.html', context)

 
    try:
        with transaction.atomic():
          
            category_id = request.POST.get('categoryId')

            if not category_id:
                raise ValidationError("Category is required")
            
          
            name = request.POST.get("name", "").strip()

            price = request.POST.get('price')
            if not price or not price.isdigit():
                messages.warning(request, "Enter a valid Price Money")
                return redirect('add_product')

            price = int(price)  # Convert to integer after validation
            if price < 0:
                messages.warning(request, "Enter a valid Price Money")
                return redirect('add_product')

            if not name:
                messages.error(request, "Product name cannot be empty or contain only spaces.")
                return redirect('add_product')
            if Product.objects.filter(name=name).exists():
                messages.error(request, "A product with this name already exists.")   
                return redirect('add_product')

            product = Product.objects.create(
                name=name,
                price=price,
                description=request.POST.get('description', ''),
                category_id=category_id,
                brand = request.POST.get('brand',''),
                offer=request.POST.get('offer') or None,
                is_listed=request.POST.get('is_listed') == 'on'
            )
            
        
            color = request.POST.get('color')
            
            
            variant = Variant.objects.create(
                product=product,
                color=color,
               
            )
                        
            variant_images = []
            required_images_count = 3  

            
            for j in range(1, 6): # max 5 imgs
                image_key = f'image{j}[]'
                if image_key in request.FILES:
                    images = request.FILES.getlist(image_key)
                    for image in images:
                        variant_images.append(
                            VariantImages(variant=variant, image=image)
                        )

           
            if len(variant_images) < required_images_count:
                raise ValidationError(
                    f"The variant ({product}-{color}) requires at least {required_images_count} images"
                )

            VariantImages.objects.bulk_create(variant_images) # bulk create the list of  variant images
            
            selected_category = get_object_or_404(Category, id=category_id)
            sizes = Size.objects.filter(category=selected_category).values_list('size', flat=True)
            for size in sizes:
                stock = request.POST.get(f"{size}")
                if int(stock) != 0:
                    all_zero = False  
                    break
                if not all_zero:
                    VariantSize.objects.create(
                        variant = variant,
                        size = size,
                        stock = int(stock) if stock and stock.isdigit() and int(stock) >= 0 else 0
                    )
                else:
                    messages.warning(request,"All sizes are cant be  out of stock while add a new product. Please try again!")    

            messages.success(request, "Product and variant created successfully!")
            return redirect('admin_products')
            


    except ValidationError as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
               
    categories = Category.objects.all()
    selected_category = get_object_or_404(Category, id=category_id)
    context = {
        'categories': categories,
        'category_id': category_id,
        # 'total_stock': total_stock
    }
    return render(request, 'admin_panel/add_product.html', context)


def update_product(request, slug):
    product = get_object_or_404(Product, slug=slug)
    category_id = product.category.id

    if request.method == "POST":
        # Get the new name from the form and strip whitespace
        name = request.POST.get("name", "").strip()
        
        if not name:
            messages.error(request, "Product name cannot be empty or contain only spaces.")
            return render(request, 'admin_panel/product_details.html', {'product': product})


        if Product.objects.filter(name=name).exclude(slug=slug).exists():
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
        return redirect('admin_product_view',slug=slug)

    return render(request, 'admin_panel/product_details.html', {'product': product})




def Shop(request):
   
    categories = Category.objects.filter(is_listed=True)
    category_ids = request.GET.getlist('category_ids') 
    # selected_sizes = request.GET.getlist('sizes')
    category_ids = [int(cid) for cid in category_ids if cid.isdigit()]
    brand_names = request.GET.getlist('brand_ids')
    
    selected_categories = Category.objects.filter(id__in=category_ids, is_listed=True) 
 
    query = request.GET.get('qry','')
    sortby= request.POST.get('sortby','name')
   
    
    if request.method == 'POST' and sortby:
        if sortby == 'popular':
           top_selling_products = (
                OrderItems.objects.values('product__id') 
                .annotate(total_quantity=Sum('quantity'))  
                .order_by('-total_quantity')  
                .values_list('product__id', flat=True)  
            )
           
           products = Product.objects.filter(id__in=top_selling_products, is_listed=True).prefetch_related(
               Prefetch('variants',queryset=Variant.objects.filter(is_listed=True))
           )
        else:
            products = Product.objects.filter(is_listed = True).prefetch_related(
                Prefetch('variants', queryset= Variant.objects.filter(is_listed=True))
            ).order_by(sortby)
       
    elif request.method == 'GET': 

        if  query:
            products =Product.objects.filter(
                Q(name__icontains=query) | Q(brand__istartswith=query) | Q(category__name__istartswith=query) 
                ).order_by('category')             
        elif category_ids: 
            products = Product.objects.filter(Q(is_listed=True) & Q(category__in=selected_categories)  ).prefetch_related(
                Prefetch('variants', queryset= Variant.objects.filter(is_listed=True))
            ).order_by('name')
            if brand_names:
                products = products.filter(Q(brand__in=brand_names))
        elif brand_names:
                 products = Product.objects.filter(Q(is_listed=True) & (Q(brand__in=brand_names)) ).prefetch_related(
                Prefetch('variants', queryset= Variant.objects.filter(is_listed=True))
            ).order_by('name')
        else:
             products = Product.objects.filter(is_listed=True).prefetch_related(
                Prefetch('variants', queryset= Variant.objects.filter(is_listed=True))
            ).order_by('name')             
        
    
    context = {
        'products': products,
        'categories': categories,
        'query':query,
        'category_ids':category_ids,
        'brand_names':brand_names,
        
    }
    return render(request, 'shop.html', context)



def userProductView(request,variant_size_slug):
    variant_size = get_object_or_404(VariantSize, slug=variant_size_slug)
    variant  = variant_size.variant
    product = variant.product
    category = product.category
    images = variant.images.all() if variant else []
    # reviews = product.reviews.all()
   
    sizes = Size.objects.filter(category=category).values_list('size', flat=True)  # it return a list of sizes

    products = Product.objects.filter(is_listed = True)
    related_products = Product.objects.filter(Q(category = category) & Q(is_listed=True)).exclude(id=product.id)[:4]
    
    offer = category.offer if category.offer >= product.offer else product.offer
    offer_price = round(product.price * (1 - offer / 100),2)


    context = {
        'product':product,
        'category':category,
        'variant' : variant,
        'variant_size':variant_size,
        'images' : images,
        'sizes' : sizes,
        'products': products,
        'related_products':related_products,
        'offer_price':offer_price,
        "offer":offer,
        # 'reviews':reviews
    }
    return render(request, 'product.html', context)

def adminProductView(request, slug):
    product = get_object_or_404(Product, slug=slug)
    variants = product.variants.prefetch_related('images').all()
    total_stock = Variant.objects.annotate(total_stock=Sum('sizes__stock'))
    context = {
        'product': product,
        'variants': variants,
        'total_stock':total_stock
    }
    return render(request, 'admin_panel/product_details.html', context)

def list_unlist_product(request,slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == "POST":
        product.is_listed = not product.is_listed
        product.save()
    return redirect('admin_products')


def update_variant(request, variant_slug ):

    variant = get_object_or_404(Variant, slug=variant_slug )   
    category_name = variant.product.category.name
    category = variant.product.category
    existing_images = variant.images.all()
    sizes = variant.sizes.all()
    variants =variant.sizes.all()
    if request.method == 'POST':
        # Update variant fields
        variant.color = request.POST.get('color')
        variant.save()
        sizes = Size.objects.filter(category=category).values_list('size', flat=True)
        for size in sizes:
            stock = request.POST.get(f"{size}")
            
            variant_size = get_object_or_404(VariantSize, variant=variant, size=size)
            variant_size.stock = stock if stock is not None and stock.isdigit() and int(stock) >= 0 else 0
            variant_size.save()
        
        variant_images = []
       
        for i in range(1,6):
            image_key = f'image{i}[]'
            if image_key in request.FILES:
                images = request.FILES.getlist(image_key)
                for image in images:
                    variant_images.append(
                        VariantImages(variant=variant, image=image)
                    )         
                           
        VariantImages.objects.bulk_create(variant_images)
        
        if variant_images :
            return redirect('variant_edit',variant.slug)
        else:
            return redirect('admin_product_view',variant.product.slug)
    
    context = {
        'variant':variant,
        'variants': variants,
        'existing_images':existing_images,
        'sizes':sizes,  
        
    }
    return render(request, 'admin_panel/edit_variant.html',context)



def add_variant(request, slug):
    product = get_object_or_404(Product, slug=slug)
    category_name = product.category.name
    category = product.category
    sizes = Size.objects.filter(category=category).values_list('size', flat=True) # it return a list of sizes
    if request.method == "POST":
        
        color = request.POST.get('color')
      
        variant = Variant.objects.create(
                product=product,
                color=color,
                # stock=stock
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

        selected_category = get_object_or_404(Category, id=product.category.id)
        sizes = Size.objects.filter(category=selected_category).values_list('size', flat=True)
        for size in sizes:
            stock = request.POST.get(f"{size}")
            if stock is not None and stock.isdigit() and int(stock) > 0:
                VariantSize.objects.create(
                    variant = variant,
                    size = size,
                    stock = int(stock),
                )    

        messages.success(request, "Variant created successfully!")
        return redirect('admin_product_view', slug=slug)
                
    context = {
        'product':product,
        'sizes':sizes
        
    }    

    return render(request, 'admin_panel/add_variant.html', context)


def delete_variant(request,variant_slug):
    variant = get_object_or_404(Variant, slug=variant_slug)
    if request.method == "POST":
        variant.is_listed = not variant.is_listed
        variant.save()
    return redirect('admin_product_view',slug=variant.product.slug)

def delete_image(request, image_id):
    image = get_object_or_404(VariantImages, id=image_id)
    variant = image.variant
    if request.method == 'POST':
        if variant.images.count() <= 3:
            messages.warning(request, "Minimum 3 images required . Add more images !")
        else:
            image.delete()
            messages.success(request, "Image deleted auccess")
            
    return redirect('variant_edit',variant_slug=variant.slug)