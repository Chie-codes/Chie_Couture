from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Store, Product, Cart, CartItem, Review, Order, PasswordResetToken

User = get_user_model()

# --------------------------
# User & Store Tests
# --------------------------
class UserAndStoreTests(TestCase):
    def setUp(self):
        self.vendor = User.objects.create_user(username="vendor", password="pass", role="vendor")
        self.store = Store.objects.create(name="Test Store", owner=self.vendor)

    def test_store_created(self):
        self.assertEqual(self.store.owner.username, "vendor")


# --------------------------
# Product & Cart Tests
# --------------------------
class ProductAndCartTests(TestCase):
    def setUp(self):
        self.buyer = User.objects.create_user(username="buyer", password="pass", role="buyer")
        self.vendor = User.objects.create_user(username="vendor", password="pass", role="vendor")
        self.store = Store.objects.create(name="Test Store", owner=self.vendor)
        self.product = Product.objects.create(store=self.store, name="Shirt", price=50, stock=10)
        self.cart = Cart.objects.create(user=self.buyer)

    def test_add_to_cart(self):
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)
        self.assertEqual(self.cart.items.count(), 1)

    def test_checkout_creates_order(self):
        item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)
        order = Order.objects.create(user=self.buyer, total=100)
        self.assertEqual(order.user.username, "buyer")
        self.assertEqual(item.quantity, 2)


# --------------------------
# Review Tests
# --------------------------
class ReviewTests(TestCase):
    def setUp(self):
        self.buyer = User.objects.create_user(username="buyer", password="pass", role="buyer")
        self.vendor = User.objects.create_user(username="vendor", password="pass", role="vendor")
        self.store = Store.objects.create(name="Test Store", owner=self.vendor)
        self.product = Product.objects.create(store=self.store, name="Shirt", price=50, stock=10)

    def test_leave_review(self):
        review = Review.objects.create(product=self.product, user=self.buyer, rating=5, comment="Great!")
        self.assertEqual(review.rating, 5)


# --------------------------
# Password Reset Tests
# --------------------------
class PasswordResetTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="resetuser", password="pass", email="a@b.com")

    def test_token_validity(self):
        token = PasswordResetToken.objects.create(user=self.user)
        self.assertTrue(token.is_valid())
        token.created_at = timezone.now() - timezone.timedelta(days=2)
        self.assertFalse(token.is_valid())


# --------------------------
# General View Tests
# --------------------------
class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="pass")

    def test_homepage_loads(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_register_user(self):
        response = self.client.post(
            reverse("register"),
            {"username": "newuser", "email": "test@a.com", "role": "buyer",
             "password1": "Complexpass123", "password2": "Complexpass123"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="newuser").exists())


# --------------------------
# Twitter Integration Tests (live)
# --------------------------
class TwitterIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.vendor = User.objects.create_user(
            username="vendor", password="pass", role="vendor"
        )
        self.client.login(username="vendor", password="pass")

    def test_create_store_triggers_tweet(self):
        response = self.client.post(
            reverse("create_store"),
            {"name": "LiveStore", "description": "Testing live Twitter"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Store.objects.filter(name="LiveStore").exists())

    def test_add_product_triggers_tweet(self):
        store = Store.objects.create(name="VendorStore", owner=self.vendor)
        response = self.client.post(
            reverse("add_product"),
            {"name": "LiveProduct", "price": 20, "stock": 5}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Product.objects.filter(name="LiveProduct").exists())

    def test_tweet_failure_does_not_block_store_creation(self):
        response = self.client.post(
            reverse("create_store"),
            {"name": "LiveStore", "description": "This may fail on Twitter"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Store.objects.filter(name="LiveStore").exists())
