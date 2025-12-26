"""Permissions of Event objects and sub objects."""
from rest_framework.permissions import (BasePermission,
                                        SAFE_METHODS,)
from core.models import EventRegistration

class CanRegisterToEvent(BasePermission):
    """Allows author and participant register to Event Registration."""
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        
        return user.role in (user.Role.AUTHOR, user.Role.PARTICIPANT)