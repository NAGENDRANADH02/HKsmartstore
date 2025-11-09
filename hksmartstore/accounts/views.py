from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.db.models import Q
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import random

from .models import Customer, Vendor, UserProfile
from .utils import generateRandomToken, sendEmailToken, sendOTPtoEmail


# -------------------------------
# CUSTOMER REGISTRATION (With Referral Logic)
# -------------------------------


def register_customer(request):
    """Handles customer registration with referral code support."""

    # ✅ Accept referral from querystring or POST
    ref_code = request.GET.get('ref') or request.POST.get('referral_code')
    referred_by_profile = None

    if ref_code:
        ref_code = ref_code.strip().upper()  # Normalize code
        referred_by_profile = UserProfile.objects.filter(referral_code__iexact=ref_code).first()

    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')

        # ✅ Prevent duplicates
        if Customer.objects.filter(Q(email=email) | Q(phone_number=phone_number)).exists() \
            or Vendor.objects.filter(Q(email=email) | Q(phone_number=phone_number)).exists():
            messages.warning(request, "Account already exists with this email or phone number.")
            return redirect('/accounts/login/')

        # ✅ Create customer user
        token = generateRandomToken()
        user = Customer.objects.create(
            username=phone_number,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            email_token=token
        )
        user.set_password(password)
        user.save()

        # ✅ Link or create profile correctly
        profile, created = UserProfile.objects.get_or_create(user=user)

        # Only set referral if not already linked
        if referred_by_profile and not profile.referred_by:
            profile.referred_by = referred_by_profile
            profile.save(update_fields=['referred_by'])

        # ✅ Send email verification
        sendEmailToken(email, token)
        messages.success(request, "Verification email sent! Please check your inbox.")
        return redirect('/accounts/login/')

    return render(request, 'accounts/customer_register.html', {
        'ref_code': ref_code or ''
    })

# -------------------------------
# CUSTOMER LOGIN
# -------------------------------
def login_customer(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = Customer.objects.get(email=email)
        except Customer.DoesNotExist:
            messages.warning(request, "No account found with this email.")
            return redirect('/accounts/login/')

        if not user.is_verified:
            messages.warning(request, "Please verify your email before logging in.")
            return redirect('/accounts/login/')

        auth_user = authenticate(request, username=user.username, password=password)

        if auth_user is not None:
            auth_login(request, auth_user)
            messages.success(request, f"Welcome back, {user.first_name or user.email}!")
            return redirect('/')
        else:
            messages.error(request, "Invalid email or password.")
            return redirect('/accounts/login/')

    return render(request, 'accounts/customer_login.html')


# -------------------------------
# VENDOR REGISTRATION
# -------------------------------
def register_vendor(request):
    """Handles vendor registration and conversion from customer to vendor safely."""
    
    if request.method == "GET":
        # If user is logged in (customer), pre-fill details
        if request.user.is_authenticated and hasattr(request.user, 'customer'):
            return render(request, 'accounts/vendor_register.html', {
                'prefilled_email': request.user.email,
                'prefilled_phone': request.user.phone_number,
                'prefilled_name': request.user.first_name,
            })
        return render(request, 'accounts/vendor_register.html')

    elif request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')
        business_name = request.POST.get('business_name')

        if not all([email, password, business_name, phone_number]):
            messages.warning(request, "Please complete all required fields.")
            return redirect('/accounts/vendor/register/')

        if Vendor.objects.filter(Q(email=email) | Q(phone_number=phone_number)).exists():
            messages.warning(request, "A vendor with this email or phone already exists.")
            return redirect('/accounts/vendor/register/')

        # ✅ Upgrade existing customer to vendor
        existing_customer = Customer.objects.filter(Q(email=email) | Q(phone_number=phone_number)).first()
        if existing_customer:
            vendor = Vendor.objects.create(
                username=existing_customer.username,
                first_name=first_name or existing_customer.first_name,
                last_name=last_name or existing_customer.last_name,
                email=existing_customer.email,
                phone_number=existing_customer.phone_number,
                business_name=business_name,
                is_verified=True,
            )
            vendor.set_password(password)
            vendor.save()

            messages.success(request, "Vendor account created successfully. You can now log in as a vendor.")
            return redirect('/accounts/vendor/login/')

        # ✅ New vendor registration
        token = generateRandomToken()
        vendor = Vendor.objects.create(
            username=phone_number,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            business_name=business_name,
            email_token=token
        )
        vendor.set_password(password)
        vendor.save()

        sendEmailToken(email, token)
        messages.success(request, "Verification email sent to your vendor email.")
        return redirect('/accounts/vendor/login/')


# -------------------------------
# VENDOR LOGIN
# -------------------------------
def login_vendor(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            vendor = Vendor.objects.get(email=email)
        except Vendor.DoesNotExist:
            messages.error(request, "No vendor found with this email.")
            return redirect('/accounts/vendor/login/')

        if not vendor.is_verified:
            messages.warning(request, "Please verify your email before login.")
            return redirect('/accounts/vendor/login/')

        auth_vendor = authenticate(request, username=vendor.username, password=password)

        if auth_vendor is not None:
            logout(request)
            auth_login(request, auth_vendor)
            messages.success(request, "Vendor login successful.")
            return redirect('/dashboard/vendor/')
        else:
            messages.error(request, "Invalid credentials.")
            return redirect('/accounts/vendor/login/')

    return render(request, 'accounts/vendor_login.html')


# -------------------------------
# EMAIL VERIFICATION
# -------------------------------
def verify_email_token(request, token):
    user = None
    if Customer.objects.filter(email_token=token).exists():
        user = Customer.objects.get(email_token=token)
    elif Vendor.objects.filter(email_token=token).exists():
        user = Vendor.objects.get(email_token=token)
    else:
        return HttpResponse("Invalid or expired token.")

    user.is_verified = True
    user.email_token = None
    user.save()

    # ✅ Auto-create profile if not exists
    UserProfile.objects.get_or_create(user=user)

    messages.success(request, "Email verified successfully.")
    if isinstance(user, Vendor):
        return redirect('/accounts/vendor/login/')
    return redirect('/accounts/login/')


# -------------------------------
# OTP LOGIN (Customer Only)
# -------------------------------
def send_otp(request, email):
    try:
        user = Customer.objects.get(email=email)
    except Customer.DoesNotExist:
        messages.warning(request, "No account found with this email.")
        return redirect('/accounts/login/')

    otp = random.randint(1000, 9999)
    user.otp = otp
    user.save()

    sendOTPtoEmail(email, otp)
    messages.info(request, "OTP sent to your email.")
    return redirect(f'/accounts/verify-otp/{email}/')


def verify_otp(request, email):
    if request.method == "POST":
        otp_input = request.POST.get('otp')
        user = Customer.objects.get(email=email)

        if otp_input == str(user.otp):
            auth_login(request, user)
            messages.success(request, "OTP verified successfully. Logged in.")
            return redirect('/')
        else:
            messages.warning(request, "Invalid OTP.")
            return redirect(f'/accounts/verify-otp/{email}/')

    return render(request, 'accounts/verify_otp.html')


# -------------------------------
# LOGOUT
# -------------------------------
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('/accounts/login/')
