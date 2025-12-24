"""Serializers of papers."""
from rest_framework import serializers
from core.models import Paper


class PaperCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paper
        fields = [
            "id",
            "title",
            "abstract",
            "keywords",
            "paper_type",
            "pdf_file",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "status", "created_at"]

    def validate_pdf_file(self, value):
        if value is None:
            raise serializers.ValidationError("PDF file is required.")

        if hasattr(value, "content_type") and value.content_type != "application/pdf":
            raise serializers.ValidationError("Only PDF files are allowed.")

        max_mb = 10
        if value.size > max_mb * 1024 * 1024:
            raise serializers.ValidationError(f"PDF must be <= {max_mb}MB.")

        return value

class PaperReadSerializer(serializers.ModelSerializer):
    author_email = serializers.EmailField(source="author.email", read_only=True)
    event_title = serializers.CharField(source="event.title", read_only=True)

    class Meta:
        model = Paper
        fields = [
            "id",
            "title",
            "abstract",
            "keywords",
            "paper_type",
            "pdf_file",
            "status",
            "author_email",
            "event_title",
            "created_at",
        ]
        read_only_fields = fields

class PaperAdminUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paper
        fields = ["status"]
