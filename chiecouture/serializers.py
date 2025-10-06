from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Store, Product, Review

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Basic user representation for nested read-only display."""

    class Meta:
        model = User
        fields = ("id", "username", "email", "role")


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for reviews. 'verified' is read-only and set by the view."""
    user = UserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ("id", "rating", "comment", "verified", "created_at", "user")
        read_only_fields = ("verified", "created_at", "user")


class ProductSerializer(serializers.ModelSerializer):
    """Product representation; include nested read-only reviews."""
    reviews = ReviewSerializer(many=True, read_only=True)
    store = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "store",
            "name",
            "description",
            "price",
            "stock",
            "image",
            "reviews",
        )


class StoreSerializer(serializers.ModelSerializer):
    """Store representation; include nested read-only products and owner info."""
    owner = UserSerializer(read_only=True)
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Store
        fields = ("id", "name", "owner", "description", "products")
