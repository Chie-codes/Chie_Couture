from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
import uuid


class User(AbstractUser):
    """
    Custom User model with an extra 'role' field.
    Roles:
      - buyer: can browse, purchase, and review products
      - vendor: can create a store and add products
    """
    ROLE_CHOICES = (("buyer", "Buyer"), ("vendor", "Vendor"))
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="buyer")

    def __str__(self):
        return f"{self.username} ({self.role})"


class Store(models.Model):
    """A store created by a vendor (1 store per vendor)."""
    name = models.CharField(max_length=255)
    owner = models.OneToOneField("User", on_delete=models.CASCADE, related_name="store")
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to="store_logos/", blank=True, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    """Product model for items sold in a store."""
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="products/", blank=True)

    def __str__(self):
        return f"{self.name} - {self.store.name}"


class Review(models.Model):
    """Reviews left by buyers for products."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} on {self.product.name}"


class Cart(models.Model):
    """Shopping cart for buyers (1 per user)."""
    user = models.OneToOneField("User", on_delete=models.CASCADE, related_name="cart")

    def __str__(self):
        return f"Cart ({self.user.username})"


class CartItem(models.Model):
    """Individual items inside a cart."""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} × {self.product.name}"


class Order(models.Model):
    """Order created during checkout."""
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"


class OrderItem(models.Model):
    """Individual items in an order."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} × {self.product.name} (Order #{self.order.id})"


class PasswordResetToken(models.Model):
    """Token for secure password reset (expires after 24 hours)."""
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="reset_tokens")
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        """Check if token is still valid (24 hours)."""
        return timezone.now() - self.created_at < timezone.timedelta(hours=24)

    def __str__(self):
        return f"Password reset token for {self.user.username}"
