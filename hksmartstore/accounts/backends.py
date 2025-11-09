from django.contrib.auth.backends import ModelBackend
from accounts.models import Customer, Vendor

class MultiUserModelBackend(ModelBackend):
    """
    Custom backend to authenticate both Customers and Vendors.
    Django will call this during login() and it will check both models.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        for model in (Customer, Vendor):
            try:
                user = model.objects.get(username=username)
                if user.check_password(password):
                    return user
            except model.DoesNotExist:
                continue
        return None

    def get_user(self, user_id):
        for model in (Customer, Vendor):
            try:
                return model.objects.get(pk=user_id)
            except model.DoesNotExist:
                continue
        return None
