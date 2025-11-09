# dashboard/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Admin
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/vendors/', views.admin_vendors, name='admin_vendors'),
    path('admin/vendors/approve/<int:vendor_id>/', views.approve_vendor, name='approve_vendor'),
    path('admin/vendors/reject/<int:vendor_id>/', views.reject_vendor, name='reject_vendor'),
    path('admin/vendors/delete/<int:vendor_id>/', views.delete_vendor, name='delete_vendor'),
    path('admin/products/', views.admin_products, name='admin_products'),
    path('admin/products/approve/<int:product_id>/', views.approve_product, name='approve_product'),
    path('admin/products/reject/<int:product_id>/', views.reject_product, name='reject_product'),
    path('admin/customers/', views.admin_customers, name='admin_customers'),
    path('admin/orders/', views.admin_orders, name='admin_orders'),
    path('admin/categories/', views.admin_categories, name='admin_categories'),
    path('admin/banners/', views.admin_banners, name='admin_banners'),
    path('admin/products/approved/', views.admin_approved_products, name='admin_approved_products'),
    path('admin/products/delete/<int:product_id>/', views.delete_product, name='delete_product'),

    # ✅ Vendor Dashboard & Features (with proper prefix)
    path('vendor/', views.vendor_dashboard, name='vendor_dashboard'),
    path('vendor/products/', views.vendor_product_list, name='vendor_product_list'),
    path('vendor/products/add/', views.vendor_add_product, name='vendor_add_product'),
    path('vendor/orders/', views.vendor_orders, name='vendor_orders'),
    path('vendor/profile/', views.vendor_profile, name='vendor_profile'),
    path('wallet/', views.wallet_view, name='wallet_view'),
    path('referrals/', views.referrals_view, name='referrals_view'),
    path('admin/approve-subscription/<int:pk>/', views.approve_subscription, name='approve_subscription'),
    path('admin/reject-subscription/<int:pk>/', views.reject_subscription, name='reject_subscription'),

]
