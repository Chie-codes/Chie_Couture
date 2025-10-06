from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404

from .models import Store, Product, Review, OrderItem
from .serializers import StoreSerializer, ProductSerializer, ReviewSerializer
from .api_permissions import IsVendor, IsOwnerOrReadOnly


class StoreViewSet(viewsets.ModelViewSet):
    """
    /api/stores/  - list, create (vendor)
    /api/stores/{id}/ - retrieve, update, delete (owner only for write)
    """

    queryset = Store.objects.all().select_related("owner")
    serializer_class = StoreSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_permissions(self):
        # Allow creation only for vendors
        if self.action in ("create",):
            return [IsVendor()]
        return [perm() for perm in self.permission_classes]

    def perform_create(self, serializer):
        # enforce one-store-per-vendor if your Store model uses OneToOneField
        user = self.request.user
        if hasattr(user, "store"):
            # vendor already has a store
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Vendor already has a store.")
        serializer.save(owner=user)

    @action(detail=True, methods=["get"], permission_classes=[AllowAny])
    def products(self, request, pk=None):
        """List products that belong to this store."""
        store = self.get_object()
        products = store.products.all()
        serializer = ProductSerializer(products, many=True, context={"request": request})
        return Response(serializer.data)

    @products.mapping.post
    def add_product(self, request, pk=None):
        """
        Create a product under this store. Only store owner (vendor) allowed.
        """
        store = self.get_object()
        if getattr(store.owner, "id", None) != request.user.id:
            return Response(
                {"detail": "Only the store owner can add products."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = ProductSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save(store=store)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    /api/products/         - list, retrieve
    /api/products/{id}/reviews/ - GET reviews, POST review (auth required)
    """

    queryset = Product.objects.all().select_related("store")
    serializer_class = ProductSerializer

    @action(detail=True, methods=["get"], permission_classes=[AllowAny])
    def reviews(self, request, pk=None):
        product = self.get_object()
        serializer = ReviewSerializer(product.reviews.all(), many=True)
        return Response(serializer.data)

    @reviews.mapping.post
    def add_review(self, request, pk=None):
        """Authenticated users can post reviews; server sets verified flag."""
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication required."}, status=401)
        product = self.get_object()
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            # mark verified if user purchased product
            user = request.user
            # try both possible order link names: 'order__user' or 'order__buyer'
            bought = OrderItem.objects.filter(
                product=product,
            ).filter(
                order__user=user
            ).exists() or OrderItem.objects.filter(
                product=product,
            ).filter(
                order__buyer=user
            ).exists()
            review = serializer.save(user=user, verified=bought, product=product)
            out = ReviewSerializer(review)
            return Response(out.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# small helper view to list stores for a vendor id
from rest_framework.views import APIView


class VendorStoresView(APIView):
    """Return stores belonging to given vendor id (public)."""

    permission_classes = [AllowAny]

    def get(self, request, vendor_id):
        stores = Store.objects.filter(owner__id=vendor_id)
        serializer = StoreSerializer(stores, many=True)
        return Response(serializer.data)
