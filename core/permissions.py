from rest_framework.permissions import BasePermission


class IsParent(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsChild(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request, 'child_profile') and request.child_profile is not None


class IsParentOfChild(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.parent == request.user
