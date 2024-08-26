from rest_framework.permissions import BasePermission


class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_manager

class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser
