from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from accounts.models import UserProfile, WalletTransaction
from .models import Notification


# ============================================================
# 🔹 Send Notification (Universal)
# ============================================================
def send_notification(user, title, message):
    """Create a notification for any user type (Customer, Vendor, or Admin)."""
    if not user:
        return
    try:
        Notification.objects.create(
            user=user,
            title=title,
            message=message
        )
    except Exception as e:
        print(f"⚠️ Notification creation failed for {user}: {e}")


# ============================================================
# 🔹 Referral Commission Distributor
# ============================================================
from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from accounts.models import UserProfile, WalletTransaction
from .models import Notification
 

@transaction.atomic
def distribute_commission(buyer, amount, commission_rate=Decimal('10.0'), min_threshold=Decimal('1.0')):
    """
    Distributes referral commission to upline chain:
    Level 1 = 10%, Level 2 = 5%, Level 3 = 2.5%, ...
    """
    print(f"💸 Starting commission distribution for {buyer.username} | Amount: ₹{amount}")

    try:
        buyer_profile = UserProfile.objects.select_related('referred_by').get(user=buyer)
    except UserProfile.DoesNotExist:
        print("⚠️ Buyer profile missing. Skipping commission.")
        return

    referrer = buyer_profile.referred_by
    current_rate = commission_rate
    level = 1

    while referrer and current_rate >= min_threshold:
        commission = (amount * current_rate / Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        print(f"💰 Crediting Level {level}: {referrer.user.username} ₹{commission} ({current_rate}%)")

        try:
            # ✅ STEP 1 — Credit wallet immediately
            referrer.wallet_balance = (referrer.wallet_balance + commission).quantize(Decimal('0.00'))
            referrer.save(update_fields=['wallet_balance'])

            # ✅ STEP 2 — Create wallet transaction
            WalletTransaction.objects.create(
                user=referrer.user,
                amount=commission,
                transaction_type='credit',
                description=f"Referral Level {level}: {current_rate}% from {buyer.username}"
            )

        except Exception as e:
            print(f"⚠️ Wallet update failed for {referrer.user.username}: {e}")
            # Force rollback if wallet update fails
            raise transaction.TransactionManagementError(e)

        # ✅ STEP 3 — Try notification (safe, non-blocking)
        try:
            Notification.objects.create(
                user=referrer.user,
                title="Referral Reward Earned",
                message=f"You earned ₹{commission} ({current_rate}% from {buyer.username}'s purchase)."
            )
        except Exception as e:
            print(f"⚠️ Notification skipped for {referrer.user.username}: {e}")

        # ✅ Move to next upline
        referrer = referrer.referred_by
        current_rate = current_rate / Decimal('2')
        level += 1

    print(f"✅ Commission distribution completed for {buyer.username}")
