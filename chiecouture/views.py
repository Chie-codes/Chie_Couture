import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import DeleteView
from django.urls import reverse_lazy

from rest_framework import generics, permissions

from .twitter_client import tweet_new_store, tweet_new_product
from .models import (
    Product,
    Store,
    Cart,
    CartItem,
    Review,
    Order,
    OrderItem,
    PasswordResetToken,
    User,
)
from .forms import UserRegisterForm, ProductForm, ReviewForm, StoreForm
from .serializers import ReviewSerializer

logger = logging.getLogger(__name__)

# -------------------------
# General Views
# -------------------------
def home(request):
    stores = Store.objects.all()
    return render(request, "home.html", {"stores": stores})

def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            if user.role == "buyer":
                Cart.objects.create(user=user)
            return redirect("home")
    else:
        form = UserRegisterForm()
    return render(request, "register.html", {"form": form})

def store_list(request):
    stores = Store.objects.all()
    return render(request, "store_list.html", {"stores": stores})

def store_detail(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    products = store.products.all()
    return render(request, "store_detail.html", {"store": store, "products": products})

# -------------------------
# Store & Vendor Views
# -------------------------
@login_required
def create_store(request):
    if request.user.role != "vendor":
        return redirect("home")
    if hasattr(request.user, "store"):
        return redirect("store_dashboard")
    if request.method == "POST":
        form = StoreForm(request.POST, request.FILES)
        if form.is_valid():
            store = form.save(commit=False)
            store.owner = request.user
            store.save()
            try:
                logo_path = store.logo.path if store.logo else None
                tweet_new_store(store_name=store.name, description=store.description, logo_path=logo_path)
            except Exception:
                pass
            return redirect("store_dashboard")
    else:
        form = StoreForm()
    return render(request, "create_store.html", {"form": form})

@login_required
def edit_store(request):
    if request.user.role != "vendor":
        return redirect("home")
    store = getattr(request.user, "store", None)
    if not store:
        return redirect("create_store")
    if request.method == "POST":
        form = StoreForm(request.POST, request.FILES, instance=store)
        if form.is_valid():
            form.save()
            messages.success(request, "Store updated successfully.")
            return redirect("store_dashboard")
    else:
        form = StoreForm(instance=store)
    return render(request, "edit_store.html", {"form": form, "store": store})

class StoreDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Store
    template_name = 'store_confirm_delete.html'
    success_url = reverse_lazy('store_dashboard')

    def test_func(self):
        store = self.get_object()
        return self.request.user == store.owner or self.request.user.is_staff

@login_required
def store_dashboard(request):
    if request.user.role != "vendor":
        return redirect("home")
    if not hasattr(request.user, "store"):
        return redirect("create_store")
    store = request.user.store
    products = store.products.all()
    reviews = Review.objects.filter(product__store=store).order_by("-created_at")
    return render(request, "store_dashboard.html", {"store": store, "products": products, "reviews": reviews})

@login_required
def add_product(request):
    if request.user.role != "vendor":
        return redirect("home")
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.store = request.user.store
            product.save()
            try:
                tweet_new_product(
                    store_name=product.store.name,
                    product_name=product.name,
                    description=product.description
                )
            except Exception:
                pass
            return redirect("store_dashboard")
    else:
        form = ProductForm()
    return render(request, "add_product.html", {"form": form})

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, store__owner=request.user)
    product.delete()
    return redirect("store_dashboard")

@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('store_dashboard')
    else:
        form = ProductForm(instance=product)
    return render(request, 'edit_product.html', {'form': form, 'product': product})

# -------------------------
# Product & Review Views
# -------------------------
def product_list(request):
    products = Product.objects.all()
    return render(request, "product_list.html", {"products": products})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all().order_by("-created_at")
    if request.method == "POST" and request.user.is_authenticated:
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.verified = product.orderitem_set.filter(order__user=request.user).exists()
            review.save()
            return redirect("product_detail", product_id=product.id)
    else:
        form = ReviewForm()
    return render(request, "product_detail.html", {"product": product, "reviews": reviews, "form": form})

class ProductReviewsListView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        product_id = self.kwargs["pk"]
        return Review.objects.filter(product_id=product_id)
    
@login_required
def vendor_reviews(request):
    # Only vendors can access
    if request.user.role != "vendor":
        return redirect("home")

    # Get vendor's store
    store = getattr(request.user, "store", None)
    if not store:
        messages.warning(request, "You don't have a store yet.")
        return redirect("create_store")

    # Get all reviews for products in this store
    reviews = Review.objects.filter(product__store=store).order_by("-created_at")

    return render(request, "vendor_reviews.html", {"store": store, "reviews": reviews})


# -------------------------
# Cart & Checkout Views
# -------------------------
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    quantity = int(request.POST.get("quantity", 1))
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
    cart_item.save()
    return redirect("cart")

@login_required
def update_cart(request):
    if request.method == "POST":
        for key, value in request.POST.items():
            if key.startswith("quantity_"):
                try:
                    item_id = int(key.split("_")[1])
                    quantity = int(value)
                    item = CartItem.objects.get(id=item_id, cart__user=request.user)
                    if quantity > 0:
                        item.quantity = quantity
                        item.save()
                    else:
                        item.delete()
                except (ValueError, CartItem.DoesNotExist):
                    continue
        return redirect("cart")
    return redirect("cart")

@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related("product")
    total = sum(item.product.price * item.quantity for item in items)
    return render(request, "cart.html", {"items": items, "total": total})

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.info(request, "Item removed from cart.")
    return redirect("cart")

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    items = cart.items.select_related("product")
    if not items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect("cart")
    if request.method == "POST":
        order = Order.objects.create(user=request.user, total=0)
        total = 0
        for item in items:
            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity, price=item.product.price)
            total += item.product.price * item.quantity
        order.total = total
        order.save()
        invoice_lines = [f"Invoice for Order #{order.id}\n\n"]
        for order_item in order.items.all():
            line = f"- {order_item.product.name} (x{order_item.quantity}) = ${order_item.price * order_item.quantity:.2f}"
            invoice_lines.append(line)
        invoice_lines.append(f"\nTotal: ${order.total:.2f}")
        invoice_text = "\n".join(invoice_lines)
        send_mail(
            subject=f"Your Invoice - Order #{order.id}",
            message=invoice_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[request.user.email],
            fail_silently=False,
        )
        items.delete()
        messages.success(request, "Checkout complete. Invoice sent to your email.")
        return redirect("product_list")
    return render(request, "checkout.html", {"items": items})

# -------------------------
# Password Reset Views
# -------------------------
def request_password_reset(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
            token = PasswordResetToken.objects.create(user=user)
            reset_link = request.build_absolute_uri(f"/reset_password/{token.token}/")
            send_mail(
                "Password Reset Request",
                f"Click the link to reset your password: {reset_link}",
                settings.DEFAULT_FROM_EMAIL,
                [email],
            )
            messages.success(request, "Password reset email sent.")
            return redirect("home")
        except User.DoesNotExist:
            messages.error(request, "Email not found.")
    return render(request, "request_password_reset.html")

def reset_password(request, token):
    try:
        token_obj = PasswordResetToken.objects.get(token=token)
    except PasswordResetToken.DoesNotExist:
        messages.error(request, "Invalid reset link.")
        return redirect("home")
    if not token_obj.is_valid():
        messages.error(request, "Reset link expired.")
        return redirect("home")
    if request.method == "POST":
        new_password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("reset_password", token=token)
        token_obj.user.password = make_password(new_password)
        token_obj.user.save()
        token_obj.delete()
        messages.success(request, "Password has been reset.")
        return redirect("login")
    return render(request, "reset_password.html", {"token": token})
