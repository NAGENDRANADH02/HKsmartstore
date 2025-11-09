from django.urls import path
from . import views

urlpatterns = [
    # Product listing
    path('', views.product_list, name='product_list'),

    # Category-wise listing
    path('category/<slug:slug>/', views.category_products, name='category_products'),

    # Individual product details
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),

    # Vendor product management
    path('vendor/list/', views.vendor_product_list, name='vendor_product_list'),
    path('vendor/add/', views.vendor_add_product, name='vendor_add_product'),
    path('vendor/edit/<int:product_id>/', views.vendor_edit_product, name='vendor_edit_product'),
    path('vendor/delete/<int:product_id>/', views.vendor_delete_product, name='vendor_delete_product'),

    # Wishlist
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
]
