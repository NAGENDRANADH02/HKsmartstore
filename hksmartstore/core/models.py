from django.db import models
from django.conf import settings
from accounts.models import UserProfile

User = settings.AUTH_USER_MODEL  # works for all: admin, vendor, customer


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} - {self.user}"


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, help_text="Discount in %")
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateField()
    valid_to = models.DateField()

    def __str__(self):
        return self.code


# ------------------------------------------------------------
# 🔹 PRIME SUBSCRIPTION MODEL (Updated for Auto Activation)
# ------------------------------------------------------------
class PrimeSubscription(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    agreed_terms = models.BooleanField(default=False)
    payment_status = models.BooleanField(default=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=999.00)


    def __str__(self):
        return f"{self.user.username} - {self.status}"

    # ✅ Automatically update UserProfile when approved
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            profile, _ = UserProfile.objects.get_or_create(user=self.user)
            if self.status == 'approved' and not profile.is_prime:
                profile.is_prime = True
                profile.save()
            elif self.status != 'approved' and profile.is_prime:
                # Optional: revoke Prime if status changes
                profile.is_prime = False
                profile.save()
        except Exception as e:
            print(f"[PrimeSubscription Save Error] {e}")
