from rest_framework import permissions


class IsAdminModeratorOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.role in ('moderator', 'admin')
            or request.user.is_superuser
        )


class IsAdminUserOrReadOnly(permissions.BasePermission):
    """Admin rights or readonly."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_admin_or_super_user
            or request.method in permissions.SAFE_METHODS
        )


class IsSuperuser(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_superuser
        )


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == 'admin'
        )
