from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from decimal import Decimal

from products.models import Category, Product
from accounts.models import Vendor
from .models import Notification, Coupon, PrimeSubscription
from core.utils import distribute_commission


# ------------------------------------------------------------
# 🔹 HOME PAGE
# ------------------------------------------------------------
def home(request):
    """Display home page with categories and featured products."""
    all_categories = Category.objects.all()
    featured_categories = all_categories[:3]

    category_products = []
    for category in featured_categories:
        products = Product.objects.filter(category=category, is_active=True)[:10]
        category_products.append({
            'category': category,
            'products': products
        })

    context = {
        'categories': all_categories,
        'category_products': category_products,
    }
    return render(request, 'home.html', context)


# ------------------------------------------------------------
# 🔹 SUBSCRIBE & EARN FLOW (Prime Membership)
# ------------------------------------------------------------
@login_required
def subscribe_view(request):
    """
    Shows prime plan details and accepts T&C agreement.
    On POST: require checkbox -> create/update PrimeSubscription -> redirect to payment page.
    """
    user = request.user

    # Check if user already has a subscription
    try:
        existing = PrimeSubscription.objects.get(user=user)
    except PrimeSubscription.DoesNotExist:
        existing = None

    # If already approved
    if existing and existing.status == 'approved':
        messages.info(request, "You are already a Prime member.")
        return redirect('/')

    if request.method == 'POST':
        agreed = request.POST.get('agree') == 'on'
        if not agreed:
            messages.error(request, "You must agree to the Terms & Conditions to continue.")
            return render(request, 'core/subscribe.html', {'subscription': existing})

        if existing:
            existing.agreed_terms = True
            existing.payment_status = False
            existing.status = 'pending'
            existing.save()
            subscription = existing
        else:
            subscription = PrimeSubscription.objects.create(
                user=user,
                agreed_terms=True,
                payment_status=False,
                status='pending'
            )

        return redirect('subscribe_payment')

    context = {
        'subscription': existing,
        'plan': {
            'name': 'HK SmartStore Prime',
            'price': Decimal('999.00'),
            'benefits': [
                'Exclusive Discounts on All Products',
                'Priority Delivery',
                'Early Access to Sales',
                'Special Prime-Only Offers'
            ]
        }
    }
    return render(request, 'core/subscribe.html', context)


@login_required
def subscribe_payment(request):
    """
    Placeholder for payment (Razorpay integration later)
    """
    user = request.user
    try:
        subscription = PrimeSubscription.objects.get(user=user)
    except PrimeSubscription.DoesNotExist:
        messages.error(request, "No subscription request found.")
        return redirect('subscribe_view')

    if subscription.status == 'approved':
        messages.info(request, "You are already a Prime member.")
        return redirect('/')

    if request.method == 'POST':
        subscription.payment_status = True
        subscription.status = 'pending'
        subscription.save()
        messages.success(request, "Payment successful. Awaiting admin approval.")
        return redirect('subscribe_success')

    context = {'subscription': subscription, 'plan_price': Decimal('999.00')}
    return render(request, 'core/subscribe_payment.html', context)


@login_required
def subscribe_success(request):
    """Display dynamic subscription status."""
    try:
        subscription = PrimeSubscription.objects.get(user=request.user)
    except PrimeSubscription.DoesNotExist:
        messages.error(request, "No active subscription found.")
        return redirect('/')

    # Example Prime price ₹999 (for commission logic)
    from core.utils import distribute_commission
    from decimal import Decimal
    distribute_commission(request.user, Decimal('999.00'))

    # ✅ Dynamic context
    context = {
        'subscription': subscription,
    }
    return render(request, 'core/subscribe_success.html', context)



# ------------------------------------------------------------
# 🔹 NOTIFICATIONS
# ------------------------------------------------------------
@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user)
    return render(request, 'core/notifications.html', {'notifications': notifications})


@login_required
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notifications')


@login_required
def clear_notifications(request):
    Notification.objects.filter(user=request.user).delete()
    return redirect('notifications')


# ------------------------------------------------------------
# 🔹 COUPONS
# ------------------------------------------------------------
def coupons_view(request):
    today = timezone.now().date()
    coupons = Coupon.objects.filter(is_active=True, valid_from__lte=today, valid_to__gte=today)
    return render(request, 'core/coupons.html', {'coupons': coupons})


# ------------------------------------------------------------
# 🔹 BECOME A VENDOR
# ------------------------------------------------------------
@login_required
def become_vendor(request):
    """Converts a logged-in customer into a vendor."""
    user = request.user

    if Vendor.objects.filter(email=user.email).exists():
        messages.info(request, "A vendor account with your email already exists.")
        return redirect('/dashboard/vendor/')

    if request.method != 'POST' or not request.POST.get('business_name'):
        return render(request, 'accounts/vendor_register.html', {
            'prefilled_email': user.email,
            'prefilled_phone': getattr(user, 'phone_number', ''),
            'prefilled_name': user.first_name,
        })

    business_name = request.POST.get('business_name')

    vendor_data = {
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'phone_number': getattr(user, 'phone_number', ''),
        'business_name': business_name,
        'is_verified': True,
    }

    try:
        vendor = Vendor.objects.create(**vendor_data)
        vendor.password = user.password
        vendor.save()
    except Exception as e:
        messages.error(request, f"Vendor account creation failed: {e}")
        return redirect('/')

    from django.contrib.auth import logout
    logout(request)
    messages.success(request, "Vendor account created successfully! Please log in as a vendor.")
    return redirect('/accounts/vendor/login/')


# ------------------------------------------------------------
# 🔹 SEARCH VIEW
# ------------------------------------------------------------
def search_view(request):
    query = request.GET.get('q', '').strip()
    products = []
    categories = []
    vendors = []

    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
            is_active=True
        )
        categories = Category.objects.filter(name__icontains=query)
        vendors = Vendor.objects.filter(
            Q(business_name__icontains=query) | Q(username__icontains=query)
        )

    context = {
        'query': query,
        'products': products,
        'categories': categories,
        'vendors': vendors,
    }
    return render(request, 'core/search_results.html', context)
