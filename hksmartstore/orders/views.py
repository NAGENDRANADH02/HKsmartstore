from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from products.models import Product
from .models import Cart, CartItem, Order, OrderItem, Address
from core.utils import send_notification
from accounts.models import Vendor, Customer
from django.contrib.auth import get_user_model
User = get_user_model()

# --------------------------
# 🛒 CART VIEWS
# --------------------------

@login_required(login_url='/accounts/login/')
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f"{product.name} added to cart.")
    return redirect('cart_view')


@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    total_price = sum(item.product.price for item in cart_items)
    total_discount = 0  # placeholder
    final_price = total_price - total_discount

    return render(request, 'orders/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_discount': total_discount,
        'final_price': final_price
    })


@login_required(login_url='/accounts/login/')
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect('cart_view')


@login_required(login_url='/accounts/login/')
def update_cart_quantity(request, item_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        item.quantity = quantity
        item.save()
    return redirect('cart_view')


# --------------------------
# 🧾 CHECKOUT & ORDER VIEWS
# --------------------------

@login_required
def checkout_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    total_price = sum(item.product.price for item in cart_items)
    total_discount = 0
    final_price = total_price - total_discount

    addresses = Address.objects.filter(user=request.user)

    return render(request, 'orders/checkout.html', {
        'cart_items': cart_items,
        'addresses': addresses,
        'total_price': total_price,
        'total_discount': total_discount,
        'final_price': final_price
    })


@login_required
def order_success(request, order_id):
    order = Order.objects.get(id=order_id)
    estimated_delivery = "3–5 Business Days"

    return render(request, 'orders/order_success.html', {
        'order': order,
        'estimated_delivery': estimated_delivery
    })


@login_required
def order_list_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})


# --------------------------
# 🏠 ADDRESS MANAGEMENT
# --------------------------

@login_required(login_url='/accounts/login/')
def address_list(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'orders/address_list.html', {'addresses': addresses})


@login_required(login_url='/accounts/login/')
def add_address(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        address_line_1 = request.POST.get('address_line_1')
        address_line_2 = request.POST.get('address_line_2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country', 'India')
        is_default = bool(request.POST.get('is_default', False))

        if is_default:
            request.user.addresses.update(is_default=False)

        Address.objects.create(
            user=request.user,
            full_name=full_name,
            phone=phone,
            address_line_1=address_line_1,
            address_line_2=address_line_2,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country,
            is_default=is_default
        )
        messages.success(request, "Address added successfully.")
        return redirect('address_list')

    return render(request, 'orders/add_address.html')


@login_required(login_url='/accounts/login/')
def edit_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    if request.method == 'POST':
        for field in ['full_name', 'phone', 'address_line_1', 'address_line_2', 'city', 'state', 'postal_code', 'country']:
            setattr(address, field, request.POST.get(field))
        address.is_default = bool(request.POST.get('is_default', False))
        address.save()
        messages.success(request, "Address updated successfully.")
        return redirect('address_list')
    return render(request, 'orders/edit_address.html', {'address': address})


@login_required(login_url='/accounts/login/')
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.delete()
    messages.success(request, "Address deleted successfully.")
    return redirect('address_list')


# --------------------------
# 🛍️ PLACE ORDER + NOTIFICATIONS
# --------------------------
@login_required
def place_order(request):
    """Handles order placement from checkout page (clean version)."""
    if request.method == 'POST':
        try:
            # ✅ Validate Address
            address_id = request.POST.get('selected_address_id')
            if not address_id or not address_id.isdigit():
                messages.error(request, "Please select a valid delivery address.")
                return redirect('checkout')

            payment_method = request.POST.get('payment_method', 'COD')
            address = Address.objects.filter(id=address_id, user=request.user).first()
            if not address:
                messages.error(request, "Invalid address selected.")
                return redirect('checkout')

            # ✅ Get Cart
            cart, _ = Cart.objects.get_or_create(user=request.user)
            cart_items = CartItem.objects.filter(cart=cart)
            if not cart_items.exists():
                messages.error(request, "Your cart is empty.")
                return redirect('cart_view')

            # ✅ Calculate Total
            total_price = sum(item.subtotal() for item in cart_items)

            # ✅ Create Order
            order = Order.objects.create(
                user=request.user,
                total=total_price,
                payment_method=payment_method,
                payment_status='Pending',
                shipping_address=f"{address.full_name}, {address.address_line_1}, "
                                 f"{address.city}, {address.state} - {address.postal_code}, {address.country}"
            )

            # ✅ Add Order Items
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    price=item.product.sale_price or item.product.price,
                    quantity=item.quantity
                )

            # ✅ Clear Cart
            cart_items.delete()

            # ✅ Success Redirect
            messages.success(request, "Your order has been placed successfully!")
            return redirect('order_success', order_id=order.id)

        except Exception as e:
            print("❌ ERROR IN place_order:", e)
            messages.error(request, "Something went wrong while placing your order.")
            return redirect('checkout')

    # ✅ Handle non-POST request
    return redirect('checkout')


from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from core.utils import distribute_commission
from .models import Order

def order_success(request, order_id):
    # ✅ Get the completed order
    order = get_object_or_404(Order, id=order_id)

    # ✅ Trigger referral commission only if order has a valid user and total
    if hasattr(order, 'user') and order.user and getattr(order, 'total', 0) > 0:
        try:
            distribute_commission(order.user, Decimal(order.total))
            print(f"💰 Commission distributed successfully for Order #{order.id}")
        except Exception as e:
            print(f"⚠️ Commission distribution failed for Order #{order.id}: {e}")
    else:
        print(f"ℹ️ Order #{order.id} has no valid user or amount — no commission distributed.")

    # ✅ Render order success page
    return render(request, 'orders/order_success.html', {'order': order})
