from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.text import slugify
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
from decimal import Decimal
import random, string

from accounts.models import Vendor, Customer, UserProfile, WalletTransaction
from products.models import Product, Category, ProductImage, Banner
from orders.models import Order
from core.models import PrimeSubscription
from core.utils import distribute_commission, send_notification


# ==============================================================
# 🔹 Helper — Admin Check
# ==============================================================
def is_admin(user):
    return user.is_superuser or user.is_staff


# ==============================================================
# 🔹 Smart Role-Based Redirect
# ==============================================================
@login_required
def dashboard_redirect(request):
    """Redirect user to correct dashboard based on role."""
    user = request.user
    if Vendor.objects.filter(email=user.email).exists():
        return redirect('vendor_dashboard')
    elif user.is_superuser or user.is_staff:
        return redirect('admin_dashboard')
    return redirect('home')


# ==============================================================
# 🔹 ADMIN DASHBOARD
# ==============================================================
@user_passes_test(is_admin)
def admin_dashboard(request):
    total_vendors = Vendor.objects.count()
    total_customers = Customer.objects.count()
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    subscriptions = PrimeSubscription.objects.all().order_by('-subscribed_at')

    recent_vendors = Vendor.objects.order_by('-date_joined')[:3]
    recent_products = Product.objects.order_by('-id')[:3]
    recent_customers = Customer.objects.order_by('-date_joined')[:3]

    recent_activities = []

    for vendor in recent_vendors:
        recent_activities.append({
            "activity": f"Vendor <b>{getattr(vendor, 'display_name', vendor.username)}</b> joined the platform",
            "user": "System",
            "date": vendor.date_joined.strftime("%b %d, %Y"),
            "status": "Approved",
            "badge_class": "success"
        })

    for product in recent_products:
        recent_activities.append({
            "activity": f"Product <b>{product.name}</b> added",
            "user": getattr(product.vendor, 'display_name', 'Unknown'),
            "date": getattr(product, 'created_at', None).strftime("%b %d, %Y") if hasattr(product, 'created_at') else "N/A",
            "status": "Pending",
            "badge_class": "warning text-dark"
        })

    for customer in recent_customers:
        recent_activities.append({
            "activity": f"New customer <b>{customer.username}</b> registered",
            "user": "System",
            "date": customer.date_joined.strftime("%b %d, %Y"),
            "status": "Auto",
            "badge_class": "info text-dark"
        })

    context = {
        "total_vendors": total_vendors,
        "total_customers": total_customers,
        "total_products": total_products,
        "total_orders": total_orders,
        "recent_activities": sorted(recent_activities, key=lambda x: x["date"], reverse=True)[:5],
        "subscriptions": subscriptions,
    }
    return render(request, "dashboard/admin_dashboard.html", context)


# ==============================================================
# 🔹 ADMIN — PRIME SUBSCRIPTION MANAGEMENT
# ==============================================================
@user_passes_test(is_admin)
def approve_subscription(request, pk):
    """Approve Prime Subscription, activate Prime, and distribute commission."""
    subscription = get_object_or_404(PrimeSubscription, pk=pk)

    subscription.status = 'approved'
    subscription.save()

    profile, _ = UserProfile.objects.get_or_create(user=subscription.user)
    profile.is_prime = True
    profile.save()

    send_notification(
        subscription.user,
        "🎉 Prime Subscription Approved",
        "Your HK SmartStore Prime membership is now active! Enjoy exclusive benefits!"
    )

    # Trigger commission logic
    distribute_commission(subscription.user, Decimal('999.00'))

    messages.success(
        request,
        f"✅ {subscription.user.username}'s Prime subscription approved and referral commissions distributed."
    )
    return redirect('admin_dashboard')


@user_passes_test(is_admin)
def reject_subscription(request, pk):
    subscription = get_object_or_404(PrimeSubscription, pk=pk)
    subscription.status = 'rejected'
    subscription.save()

    profile, _ = UserProfile.objects.get_or_create(user=subscription.user)
    profile.is_prime = False
    profile.save()

    send_notification(
        subscription.user,
        "❌ Prime Subscription Rejected",
        "Your Prime subscription request has been rejected by the admin."
    )

    messages.error(request, f"❌ {subscription.user.username}'s Prime subscription rejected.")
    return redirect('admin_dashboard')


# ==============================================================
# 🔹 ADMIN — VENDOR MANAGEMENT
# ==============================================================
@user_passes_test(is_admin)
def admin_vendors(request):
    vendors = Vendor.objects.all().order_by('-date_joined')
    return render(request, 'dashboard/admin_vendors.html', {'vendors': vendors})


@user_passes_test(is_admin)
def approve_vendor(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    vendor.status = 'approved'
    vendor.is_verified = True
    vendor.save()
    messages.success(request, f"{vendor.display_name} approved successfully.")
    return redirect('admin_vendors')


@user_passes_test(is_admin)
def reject_vendor(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    vendor.status = 'rejected'
    vendor.is_verified = False
    vendor.save()
    messages.warning(request, f"{vendor.display_name} rejected.")
    return redirect('admin_vendors')


@user_passes_test(is_admin)
def delete_vendor(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    vendor.delete()
    messages.error(request, "Vendor deleted successfully.")
    return redirect('admin_vendors')


# ==============================================================
# 🔹 ADMIN — PRODUCTS, CUSTOMERS, ORDERS, CATEGORIES, BANNERS
# ==============================================================
@user_passes_test(is_admin)
@never_cache
def admin_products(request):
    products = Product.objects.filter(status__in=['pending', 'rejected']).select_related('vendor').order_by('-id')
    return render(request, 'dashboard/admin_products.html', {'products': products})


@user_passes_test(is_admin)
@never_cache
def approve_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.is_active = True
    product.status = 'approved'
    product.save()
    messages.success(request, f"✅ {product.name} approved successfully.")
    return redirect('admin_products')


@user_passes_test(is_admin)
@never_cache
def reject_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.is_active = False
    product.status = 'rejected'
    product.save()
    messages.warning(request, f"❌ {product.name} rejected.")
    return redirect('admin_products')


@user_passes_test(is_admin)
def admin_customers(request):
    customers = Customer.objects.all().order_by('-date_joined')
    return render(request, 'dashboard/admin_customers.html', {'customers': customers})


@user_passes_test(is_admin)
def admin_orders(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'dashboard/admin_orders.html', {'orders': orders})


@user_passes_test(is_admin)
def admin_categories(request):
    categories = Category.objects.all()
    if request.method == "POST":
        name = request.POST.get('name')
        image = request.FILES.get('image')
        Category.objects.create(name=name, image=image, slug=slugify(name))
        messages.success(request, "Category added successfully.")
        return redirect('admin_categories')
    return render(request, 'dashboard/admin_categories.html', {'categories': categories})


@user_passes_test(is_admin)
def admin_banners(request):
    banners = Banner.objects.all()
    if request.method == "POST":
        title = request.POST.get('title')
        image = request.FILES.get('image')
        Banner.objects.create(title=title, image=image)
        messages.success(request, "Banner uploaded successfully.")
        return redirect('admin_banners')
    return render(request, 'dashboard/admin_banners.html', {'banners': banners})


@user_passes_test(is_admin)
@never_cache
def admin_approved_products(request):
    products = Product.objects.filter(status='approved').select_related('vendor').order_by('-id')
    return render(request, 'dashboard/admin_approved_products.html', {'products': products})


@user_passes_test(is_admin)
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.error(request, f"🗑️ Product '{product.name}' deleted successfully.")
    return redirect('admin_approved_products')


# ==============================================================
# 🔹 WALLET & REFERRALS
# ==============================================================
@login_required
def wallet_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    transactions = WalletTransaction.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'dashboard/wallet.html', {
        'profile': profile,
        'transactions': transactions
    })


@login_required
def referrals_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    referred_users = UserProfile.objects.filter(referred_by=profile)
    return render(request, 'dashboard/referrals.html', {
        'profile': profile,
        'referred_users': referred_users
    })


# ==============================================================
# 🔹 VENDOR DASHBOARD & MANAGEMENT
# ==============================================================
@login_required(login_url='/accounts/vendor/login/')
def vendor_dashboard(request):
    vendor = Vendor.objects.filter(email=request.user.email).first()
    if not vendor:
        messages.error(request, "Access denied. Please log in as a vendor.")
        return redirect('/accounts/vendor/login/')

    products = Product.objects.filter(vendor=vendor)
    orders = Order.objects.filter(items__product__vendor=vendor).distinct()
    total_products = products.count()
    total_orders = orders.count()
    total_revenue = sum(getattr(order, 'total', 0) for order in orders)

    context = {
        'vendor': vendor,
        'products': products,
        'orders': orders,
        'total_products': total_products,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
    }
    return render(request, 'dashboard/vendor_dashboard.html', context)


@login_required(login_url='/accounts/vendor/login/')
def vendor_product_list(request):
    vendor = Vendor.objects.filter(email=request.user.email).first()
    if not vendor:
        messages.error(request, "Access denied.")
        return redirect('/accounts/vendor/login/')

    products = Product.objects.filter(vendor=vendor).order_by('-id')
    return render(request, 'products/vendor_product_list.html', {'vendor': vendor, 'products': products})


@login_required(login_url='/accounts/vendor/login/')
def vendor_add_product(request):
    vendor = Vendor.objects.filter(email=request.user.email).first()
    if not vendor:
        messages.error(request, "Access denied.")
        return redirect('/accounts/vendor/login/')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '')
        price = request.POST.get('price') or 0
        stock = request.POST.get('stock') or 0
        category_id = request.POST.get('category')
        images = request.FILES.getlist('images')

        category = get_object_or_404(Category, id=category_id) if category_id else None

        base_slug = slugify(name) or f"product-{''.join(random.choices(string.ascii_lowercase + string.digits, k=6))}"
        slug = base_slug
        counter = 1
        while Product.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        product = Product.objects.create(
            vendor=vendor,
            category=category,
            name=name,
            description=description,
            price=price,
            stock=stock,
            slug=slug,
            is_active=False,
            status='pending'
        )

        for img in images:
            ProductImage.objects.create(product=product, image=img)

        messages.success(request, f"✅ Product '{product.name}' added successfully! Awaiting admin approval.")
        return redirect('vendor_product_list')

    categories = Category.objects.all()
    return render(request, 'products/vendor_add_product.html', {'categories': categories})


@login_required(login_url='/accounts/vendor/login/')
def vendor_orders(request):
    vendor = Vendor.objects.filter(email=request.user.email).first()
    if not vendor:
        messages.error(request, "Access denied.")
        return redirect('/accounts/vendor/login/')

    orders = Order.objects.filter(items__product__vendor=vendor).distinct()
    return render(request, 'products/vendor_orders.html', {'orders': orders, 'vendor': vendor})


@login_required(login_url='/accounts/vendor/login/')
def vendor_profile(request):
    vendor = Vendor.objects.filter(email=request.user.email).first()
    if not vendor:
        messages.error(request, "Access denied.")
        return redirect('/accounts/vendor/login/')

    if request.method == 'POST':
        vendor.business_name = request.POST.get('business_name', vendor.business_name)
        vendor.first_name = request.POST.get('first_name', vendor.first_name)
        vendor.last_name = request.POST.get('last_name', vendor.last_name)
        vendor.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('vendor_profile')

    return render(request, 'products/vendor_profile.html', {'vendor': vendor})
