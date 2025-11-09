from django.urls import path
from . import views

urlpatterns = [
    # -------------------------------
    # Customer routes
    # -------------------------------
    path('register/', views.register_customer, name='register_customer'),
    path('login/', views.login_customer, name='login'),  # ✅ renamed to match templates
    path('logout/', views.logout_view, name='logout'),   # ✅ renamed to match templates

    # -------------------------------
    # Vendor routes
    # -------------------------------
    path('vendor/register/', views.register_vendor, name='register_vendor'),
    path('vendor/login/', views.login_vendor, name='login_vendor'),

    # -------------------------------
    # Verification + OTP
    # -------------------------------
    path('verify/<str:token>/', views.verify_email_token, name='verify_email_token'),
    path('send-otp/<str:email>/', views.send_otp, name='send_otp'),
    path('verify-otp/<str:email>/', views.verify_otp, name='verify_otp'),
]
