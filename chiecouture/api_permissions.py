from rest_framework import permissions


class IsVendor(permissions.BasePermission):
    """Allow access only to authenticated users with role == 'vendor'."""

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
            and getattr(request.user, "role", None) == "vendor"
        )


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission: allow safe methods for anyone; writes only to owner.
    Works for objects that have an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return getattr(obj, "owner", None) == request.user
