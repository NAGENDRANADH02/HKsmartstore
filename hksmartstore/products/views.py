from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils.text import slugify
from accounts.models import Vendor
from .models import Product, Category, ProductImage

# -------------------- CUSTOMER SIDE --------------------

def product_list(request):
    """Display all active products with pagination and optional search"""
    query = request.GET.get('q')
    products = Product.objects.filter(is_active=True)

    if query:
        products = products.filter(name__icontains=query)

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'products/product_list.html', {
        'products': page_obj,
        'paginator': paginator,
        'page_obj': page_obj,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)

    # ✅ Get related products (same category, excluding this one)
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]  # limit to 4 items

    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'products/product_detail.html', context)


def category_products(request, slug):
    """List all products in a category"""
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, is_active=True)
    return render(request, 'products/category_products.html', {
        'category': category,
        'products': products
    })


# -------------------- VENDOR SIDE --------------------

@login_required(login_url='/accounts/vendor/login/')
def vendor_product_list(request):
    """List all products added by the logged-in vendor"""
    vendor = Vendor.objects.filter(email=request.user.email).first()
    if not vendor:
        messages.error(request, "Access denied. Please log in as a vendor.")
        return redirect('/accounts/vendor/login/')

    products = Product.objects.filter(vendor=vendor)
    return render(request, 'products/vendor_product_list.html', {'products': products})


from django.utils.text import slugify
import random
import string

@login_required(login_url='/accounts/vendor/login/')
def vendor_add_product(request):
    vendor = Vendor.objects.filter(email=request.user.email).first()
    if not vendor:
        messages.error(request, "Access denied. Please log in as a vendor.")
        return redirect('/accounts/vendor/login/')

    from products.models import Category, Product, ProductImage

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price') or 0
        category_id = request.POST.get('category')
        stock = request.POST.get('stock') or 0
        images = request.FILES.getlist('images')

        category = get_object_or_404(Category, id=category_id)

        # ✅ Generate safe slug
        base_slug = slugify(name) or f"product-{''.join(random.choices(string.ascii_lowercase + string.digits, k=6))}"
        slug = base_slug
        counter = 1
        while Product.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        # ✅ Create product
        product = Product.objects.create(
            vendor=vendor,
            name=name or f"Untitled Product {random.randint(1000,9999)}",
            description=description,
            price=price,
            stock=stock,
            category=category,
            slug=slug,
            is_active=True
        )

        # ✅ Save multiple images
        if images:
            for img in images:
                ProductImage.objects.create(product=product, image=img)

        messages.success(request, f"✅ Product '{product.name}' added successfully!")
        return redirect('vendor_product_list')

    categories = Category.objects.all()
    return render(request, 'products/vendor_add_product.html', {'categories': categories})

@login_required(login_url='/accounts/vendor/login/')
def vendor_edit_product(request, product_id):
    """Edit an existing product by the vendor"""
    vendor = Vendor.objects.filter(email=request.user.email).first()
    if not vendor:
        messages.error(request, "Access denied. Please log in as a vendor.")
        return redirect('/accounts/vendor/login/')

    # ✅ Fetch the product belonging to the vendor
    product = get_object_or_404(Product, id=product_id, vendor=vendor)
    categories = Category.objects.all()

    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')

        # ✅ Fix DecimalField empty value errors
        price = request.POST.get('price') or 0
        sale_price = request.POST.get('sale_price') or None
        stock = request.POST.get('stock') or 0

        product.price = price
        product.sale_price = sale_price
        product.stock = stock

        # ✅ Update category if changed
        category_id = request.POST.get('category')
        if category_id:
            product.category = get_object_or_404(Category, id=category_id)

        # ✅ Save updated product
        product.save()

        # ✅ Handle new image uploads (append, don’t replace)
        new_images = request.FILES.getlist('images')
        for img in new_images:
            ProductImage.objects.create(product=product, image=img)

        messages.success(request, f"✅ Product '{product.name}' updated successfully!")
        return redirect('vendor_product_list')

    images = ProductImage.objects.filter(product=product)
    return render(request, 'products/vendor_edit_product.html', {
        'product': product,
        'categories': categories,
        'images': images,
    })

@login_required(login_url='/accounts/vendor/login/')
def vendor_delete_product(request, product_id):
    """Delete a vendor’s product"""
    vendor = Vendor.objects.filter(email=request.user.email).first()
    product = get_object_or_404(Product, id=product_id, vendor=vendor)
    product.delete()
    messages.success(request, "Product deleted successfully.")
    return redirect('vendor_product_list')


# -------------------- WISHLIST --------------------

@login_required
def wishlist_view(request):
    """Display all wishlist products of the logged-in user"""
    wishlist_products = request.user.wishlist_items.all()
    return render(request, 'products/wishlist.html', {'wishlist_products': wishlist_products})


@login_required
def add_to_wishlist(request, product_id):
    """Add or remove a product from wishlist"""
    product = get_object_or_404(Product, id=product_id)
    if product.wishlist.filter(id=request.user.id).exists():
        product.wishlist.remove(request.user)
    else:
        product.wishlist.add(request.user)
    return redirect('wishlist')
