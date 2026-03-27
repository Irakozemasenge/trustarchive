from rest_framework.permissions import BasePermission


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'superadmin'


class IsAdminPartner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'superadmin']


class IsPublicOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated
