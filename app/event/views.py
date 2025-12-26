"""Views for the event APIs."""

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
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
from event.permissions import CanRegisterToEvent
from rest_framework.permissions import (IsAuthenticated,
                                        AllowAny,
                                        IsAdminUser,)

from core.models import (
    Event,
    Topic,
    EventRegistration,
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
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        """Public can read topics, and only admin users can create/update/delete."""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]

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
        
        if self.action in ['register', 'cancel_registration', 'my_registration']:
            return [IsAuthenticated(), CanRegisterToEvent()]
        
        return [IsAdminUser()]

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.EventSerializer
        
        if self.action in ['create', 'update', 'partial_update']:
            return serializers.EventSerializer
        
        if self.action == 'retrieve':
            return serializers.EventDetailSerializer
        
        if self.action in ['register', 'my_registration']:
            return serializers.EventRegistrationSerializer
        
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
    
    @action(methods=['POST'], detail=True, url_path='register')
    def register(self, request, pk=None):
        """Register the current user to this event."""
        event = self.get_object()

        serializer = self.get_serializer(
            data=request.data,
            context={'request': request, 'event': event}
        )
        serializer.is_valid(raise_exception=True)
        registration = serializer.save()

        return Response(
            serializers.EventRegistrationSerializer(registration).data,
            status=status.HTTP_201_CREATED
        )


    @register.mapping.delete
    def cancel_registration(self, request, pk=None):
        """Cancel the current user's registration for this event."""
        event = self.get_object()

        deleted, _ = EventRegistration.objects.filter(
            user=request.user,
            event=event
        ).delete()

        if deleted == 0:
            return Response(
                {'detail': 'You are not registered for this event.'},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


    @action(methods=['GET'], detail=True, url_path='my-registration')
    def my_registration(self, request, pk=None):
        """Get the current user's registration for this event (React state)."""
        event = self.get_object()

        registration = EventRegistration.objects.filter(
            user=request.user,
            event=event
        ).first()

        if not registration:
            return Response(
                {'detail': 'Not registered.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = serializers.EventRegistrationSerializer(registration)
        return Response(serializer.data, status=status.HTTP_200_OK)
