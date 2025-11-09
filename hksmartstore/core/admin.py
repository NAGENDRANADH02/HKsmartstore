from django.contrib import admin
from .models import Notification, Coupon, PrimeSubscription
from django.utils.html import format_html

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('title', 'message', 'user__username')


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount', 'is_active', 'valid_from', 'valid_to')
    list_filter = ('is_active', 'valid_from', 'valid_to')
    search_fields = ('code',)


@admin.register(PrimeSubscription)
class PrimeSubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'user', 
        'status', 
        'payment_status', 
        'agreed_terms', 
        'subscribed_at', 
        'prime_status'
    )
    list_filter = ('status', 'payment_status')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('subscribed_at',)
    actions = ['approve_subscription', 'reject_subscription']

    def prime_status(self, obj):
        """Show Prime status visually"""
        color = 'green' if obj.status == 'approved' else 'gray'
        return format_html('<span style="color:{}; font-weight:bold;">{}</span>', color, obj.status.upper())
    prime_status.short_description = "Prime Status"

    # ✅ Admin Actions
    def approve_subscription(self, request, queryset):
        for sub in queryset:
            sub.status = 'approved'
            sub.save()
        self.message_user(request, "Selected subscriptions approved successfully.")
    approve_subscription.short_description = "✅ Approve selected subscriptions"

    def reject_subscription(self, request, queryset):
        for sub in queryset:
            sub.status = 'rejected'
            sub.save()
        self.message_user(request, "Selected subscriptions rejected.")
    reject_subscription.short_description = "❌ Reject selected subscriptions"

    # ✅ Auto-update UserProfile.is_prime when saving manually
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        try:
            from accounts.models import UserProfile
            profile, _ = UserProfile.objects.get_or_create(user=obj.user)
            if obj.status == 'approved':
                profile.is_prime = True
                profile.save()
            elif obj.status != 'approved':
                profile.is_prime = False
                profile.save()
        except Exception as e:
            self.message_user(request, f"Error updating user profile: {e}", level='error')
