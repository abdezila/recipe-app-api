from rest_framework.permissions import BasePermission

class IsEventAdmin(BasePermission):
    """Allows only admin create event object"""

    def has_object_permission(self, request, view, obj):
        """admin can see and edit events."""
        if request.user.is_stuff or request.user.is_superadmin:
            return True
        
        pass