"""Views for the event APIs."""
from rest_framework import (
    viewsets,
    )
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import (IsAuthenticated,
                                        AllowAny,
                                        IsAdminUser,)

from core.models import (
    Event,
    Topic
)
from event import serializers

class TopicViewSet(viewsets.ModelViewSet):
    """View for managing global topics."""
    queryset = Topic.objects.all().order_by('-name')
    serializer_class = serializers.TopicSerializer

    def get_permissions(self):
        """Public can read topics, and only admin users can create/update/delete."""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]
    
class EventViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""
    serializer_class = serializers.EventDetailSerializer
    queryset = Event.objects.all().order_by('-id')
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        """Custom permissions."""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.EventSerializer
        
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new event"""
        serializer.save(user = self.request.user)