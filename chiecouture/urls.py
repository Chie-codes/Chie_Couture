from django.urls import path
from . import views
from .views import ProductReviewsListView, StoreDeleteView, vendor_reviews
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    # Home & Auth
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),

    # Store
    path("store/create/", views.create_store, name="create_store"),
    path('store/edit/', views.edit_store, name='edit_store'),
    path("store/dashboard/", views.store_dashboard, name="store_dashboard"),
    path("stores/", views.store_list, name="store_list"),
    path("stores/<int:store_id>/", views.store_detail, name="store_detail"),
    path('stores/<int:pk>/delete/', StoreDeleteView.as_view(), name='store-delete'),
    path("store/reviews/", vendor_reviews, name="vendor-reviews"),

    # Products
    path("products/", views.product_list, name="product_list"),
    path("products/<int:product_id>/", views.product_detail, name="product_detail"),
    path("products/add/", views.add_product, name="add_product"),
    path('products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path("products/delete/<int:product_id>/", views.delete_product, name="delete_product"),
    path("products/<int:pk>/reviews/", ProductReviewsListView.as_view(), name="product-reviews"),

    # Cart & Checkout
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:item_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("cart/update/", views.update_cart, name="update_cart"),



    # Password Reset
    path("request_password_reset/", views.request_password_reset, name="request_password_reset"),
    path("reset_password/<uuid:token>/", views.reset_password, name="reset_password"),
]
