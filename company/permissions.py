from rest_framework.permissions import BasePermission


class IsManager(BasePermission):
    message = 'Given User is not a manager.'
    def has_permission(self, request, view):
        return request.user.is_manager

    def has_object_permission(self, request, view, obj):
        try:
            if request.user.is_manager and obj.hasAttribute("company_id") and request.user.hasAttribute("company_id") and obj.company_id == request.user.company_id:
                return True
            else:
                return request.user.is_superuser
        except AttributeError:
            return request.user.is_superuser


class IsSuperUser(BasePermission):
    message = 'Given User is not a SuperUser.'
    def has_permission(self, request, view):
        return request.user.is_superuser
