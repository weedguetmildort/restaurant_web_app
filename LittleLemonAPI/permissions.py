from rest_framework.permissions import BasePermission, IsAdminUser

class IsManager(BasePermission):
    def has_permission(self, request, view):
        is_admin = IsAdminUser().has_permission(request, view)
        is_manager = request.user and request.user.groups.filter(name='Manager').exists()
        return is_admin or is_manager
