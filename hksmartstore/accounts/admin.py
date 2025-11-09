from django.contrib import admin
from .models import Customer, Vendor
from django.contrib import admin
from .models import UserProfile, WalletTransaction


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone_number', 'is_verified')
    search_fields = ('username', 'email', 'phone_number')

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'business_name', 'is_verified')
    search_fields = ('username', 'email', 'business_name')
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_prime', 'wallet_balance', 'referral_code', 'referred_by')
    search_fields = ('user__username', 'referral_code')

@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'transaction_type', 'description', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('user__username', 'description')
