from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as drf_authtoken_views

from .api_views import StoreViewSet, ProductViewSet, VendorStoresView

router = DefaultRouter()
router.register(r"stores", StoreViewSet, basename="store")
router.register(r"products", ProductViewSet, basename="product")

urlpatterns = [
    path("", include(router.urls)),
    # vendor -> stores listing
    path("vendors/<int:vendor_id>/stores/", VendorStoresView.as_view(), name="vendor_stores"),
    # token endpoint
    path("api-token-auth/", drf_authtoken_views.obtain_auth_token, name="api_token_auth"),
]
