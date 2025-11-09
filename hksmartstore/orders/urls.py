from django.urls import path
from . import views

urlpatterns = [
    # cart
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('place-order/', views.place_order, name='place_order'),


    # orders
    path('checkout/', views.checkout_view, name='checkout'),
    path('order/success/<int:order_id>/', views.order_success, name='order_success'),
    path('orders/', views.order_list_view, name='order_list'),
    path('order/<int:order_id>/', views.order_detail_view, name='order_detail'),

    # address management
    path('addresses/', views.address_list, name='address_list'),
    path('addresses/add/', views.add_address, name='add_address'),
    path('addresses/edit/<int:address_id>/', views.edit_address, name='edit_address'),
    path('addresses/delete/<int:address_id>/', views.delete_address, name='delete_address'),

]
