from django.db import models
from django.conf import settings
from products.models import Product

User = settings.AUTH_USER_MODEL


# --------------------
# Cart Model
# --------------------
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cart"

    def __str__(self):
        return f"Cart of {self.user.username}"

    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    def total_price(self):
        return sum(item.subtotal() for item in self.items.all())


# --------------------
# Cart Item Model
# --------------------
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = "cart_item"
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"

    def subtotal(self):
        price = self.product.sale_price or self.product.price
        return price * self.quantity


# --------------------
# Order Model
# --------------------
# --------------------
# Order Model (Updated)
# --------------------
class Order(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
        ('COD', 'Cash on Delivery'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('COD', 'Cash on Delivery'),
        ('Online', 'Online Payment'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='COD')
    payment_id = models.CharField(max_length=255, blank=True, null=True)  # Razorpay order/payment id
    shipping_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "order"

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

    def total_items(self):
        return sum(item.quantity for item in self.items.all())



# --------------------
# Order Item Model
# --------------------
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = "order_item"

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def subtotal(self):
        return self.price * self.quantity

# --------------------
# Address Model
# --------------------
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='India')
    is_default = models.BooleanField(default=False)

    class Meta:
        db_table = "address"

    def __str__(self):
        return f"{self.full_name}, {self.city}"
