"""Views for the event APIs."""
from rest_framework import (
    viewsets,
    )
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import (
    Event
)
from event import serializers

class EventViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""
    serializer_class = serializers.EventDetailSerializer
    queryset = Event.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve events for authenticted user."""
        return self.queryset.filter(user= self.request.user).order_by('-id')
    
    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.EventSerializer
        
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new event"""
        serializer.save(user = self.request.user)