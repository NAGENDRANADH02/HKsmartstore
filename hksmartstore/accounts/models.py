from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

# ---------------------------------------------------
# Base User model (common for both Customer & Vendor)
# ---------------------------------------------------
class BaseUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    email_token = models.CharField(max_length=100, blank=True, null=True)
    otp = models.CharField(max_length=10, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    
    # Role Flags
    is_vendor = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)

    # Tracking fields
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # Prevent table creation for BaseUser

    def __str__(self):
        return f"{self.username} ({self.email})"


# ---------------------------------------------------
# Customer Model
# ---------------------------------------------------
class Customer(BaseUser):
    is_customer = True

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customer_set',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customer_permission_set',
        blank=True
    )

    class Meta:
        db_table = "customer"
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.username} (Customer)"


# ---------------------------------------------------
# Vendor Model
# ---------------------------------------------------
class Vendor(BaseUser):
    is_vendor = True

    business_name = models.CharField(max_length=255, blank=True, null=True)
    gst_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='vendor_set',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='vendor_permission_set',
        blank=True
    )

    class Meta:
        db_table = "vendor"
        verbose_name = "Vendor"
        verbose_name_plural = "Vendors"
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.business_name or self.username} (Vendor)"

    @property
    def display_name(self):
        """Returns vendor's display name safely."""
        return self.business_name or f"{self.first_name or self.username}'s Store"


# ---------------------------------------------------
# User Profile — For Referrals, Wallet, and Prime
# ---------------------------------------------------
class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_prime = models.BooleanField(default=False)
    referral_code = models.CharField(max_length=10, unique=True, blank=True, null=True)
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        if not self.referral_code:
            # Generate an 8-character uppercase code
            self.referral_code = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} (Prime: {'Yes' if self.is_prime else 'No'})"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"


# ---------------------------------------------------
# Wallet Transaction Model
# ---------------------------------------------------
class WalletTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet_transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        sign = '+' if self.transaction_type == 'credit' else '-'
        return f"{self.user.username}: {sign}{self.amount}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Wallet Transaction"
        verbose_name_plural = "Wallet Transactions"


# ---------------------------------------------------
# Signals — Auto-create UserProfile for every new user
# ---------------------------------------------------
@receiver(post_save, sender=Customer)
@receiver(post_save, sender=Vendor)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
