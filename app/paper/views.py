from rest_framework.viewsets import ModelViewSet
from rest_framework.parsers import MultiPartParser, FormParser
from core.models import Paper
from .serializers import (
    PaperCreateSerializer,
    PaperReadSerializer,
    PaperAdminUpdateSerializer,
)
from .permissions import PaperPermissions


class EventPaperViewSet(ModelViewSet):
    permission_classes = [PaperPermissions]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return Paper.objects.filter(
            event_id=self.kwargs["event_id"]
        ).order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "create":
            return PaperCreateSerializer
        if self.action in ["update", "partial_update"]:
            return PaperAdminUpdateSerializer
        return PaperReadSerializer

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            event_id=self.kwargs["event_id"],
        )
