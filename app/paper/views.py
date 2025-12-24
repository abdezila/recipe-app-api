from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAdminUser

from core.models import Paper
from . import serializers
from .permissions import PaperPermissions


class EventPaperViewSet(viewsets.ModelViewSet):
    """
    /api/event/<event_id>/papers/
    - GET: list papers for this event (public)
    - POST: author creates paper (pdf upload)
    - PATCH set-status: admin accept/reject
    - POST upload-pdf: admin replace pdf (optional)
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [PaperPermissions]
    parser_classes = [MultiPartParser, FormParser]  # needed for pdf upload

    def get_queryset(self):
        return Paper.objects.filter(
            event_id=self.kwargs["event_id"]
        ).order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "create":
            return serializers.PaperCreateSerializer
        if self.action == "set_status":
            return serializers.PaperStatusSerializer
        if self.action == "upload_pdf":
            return serializers.PaperPDFSerializer
        return serializers.PaperSerializer

    def perform_create(self, serializer):
        # event comes from URL, author from authenticated user
        serializer.save(
            author=self.request.user,
            event_id=self.kwargs["event_id"],
        )

    @action(methods=["PATCH"], detail=True, url_path="set-status",
            authentication_classes=[TokenAuthentication],
            permission_classes=[IsAdminUser])
    def set_status(self, request, event_id=None, pk=None):
        """Admin: accept/reject paper by changing status."""
        paper = self.get_object()
        serializer = self.get_serializer(paper, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=True, url_path="upload-pdf",
            authentication_classes=[TokenAuthentication],
            permission_classes=[IsAdminUser])
    def upload_pdf(self, request, event_id=None, pk=None):
        """Admin: upload/replace pdf file (optional)."""
        paper = self.get_object()
        serializer = self.get_serializer(paper, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
