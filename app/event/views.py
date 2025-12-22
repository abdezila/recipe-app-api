"""Views for the event APIs."""
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from rest_framework import (
    viewsets,
    mixins,
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

class TopicViewSet(viewsets.GenericViewSet,
                   mixins.ListModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   ):
    """View for managing global topics."""
    queryset = Topic.objects.all().order_by('-name')
    serializer_class = serializers.TopicSerializer

    def get_permissions(self):
        """Public can read topics, and only admin users can create/update/delete."""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser(),IsAuthenticated()]

@extend_schema_view(
    list = extend_schema(
        parameters = [
            OpenApiParameter(
                name = 'topics',
                type = OpenApiTypes.STR,
                description = 'Comma separated list of topic IDs to filter by'
            )
        ]
    )
)
class EventViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""
    serializer_class = serializers.EventDetailSerializer
    queryset = Event.objects.all().order_by('-id')
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        """Custom permissions."""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.EventSerializer
        
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new event"""
        serializer.save(user = self.request.user)

    def _params_to_ints(self, qs):
        """Convert a comma separated string to a list of ints."""
        return [int(str_id) for str_id in qs.split(',')]
    
    def get_queryset(self):
        """Retrieve events, optionally filtered by topics."""
        queryset = self.queryset

        topics = self.request.query_params.get('topics')
        if topics:
            topic_ids = self._params_to_ints(topics)
            queryset = queryset.filter(topics__id__in = topic_ids)

        return queryset.order_by('-id').distinct()