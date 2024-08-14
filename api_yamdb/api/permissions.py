from rest_framework import permissions


class IsAdminModeratorOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.role in ('moderator', 'admin')
            or request.user.is_superuser
        )
