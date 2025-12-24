from rest_framework import serializers
from core.models import Paper


class PaperSerializer(serializers.ModelSerializer):
    """Serializer for paper list/detail (read)."""
    author_email = serializers.EmailField(source="author.email", read_only=True)
    event_title = serializers.CharField(source="event.title", read_only=True)

    class Meta:
        model = Paper
        fields = [
            "id",
            "event",
            "event_title",
            "author",
            "author_email",
            "title",
            "abstract",
            "keywords",
            "paper_type",
            "pdf_file",
            "status",
            "created_at",
        ]
        read_only_fields = fields


class PaperCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a paper (author)."""

    class Meta:
        model = Paper
        fields = ["id", "title", "abstract", "keywords", "paper_type", "pdf_file"]
        read_only_fields = ["id"]

        extra_kwargs = {
            "pdf_file": {"required": True}
        }

    def validate_pdf_file(self, value):
        if hasattr(value, "content_type") and value.content_type != "application/pdf":
            raise serializers.ValidationError("Only PDF files are allowed.")
        max_mb = 10
        if value.size > max_mb * 1024 * 1024:
            raise serializers.ValidationError(f"PDF must be <= {max_mb}MB.")
        return value


class PaperStatusSerializer(serializers.ModelSerializer):
    """Serializer for admin to accept/reject a paper."""

    class Meta:
        model = Paper
        fields = ["id", "status"]
        read_only_fields = ["id"]


class PaperPDFSerializer(serializers.ModelSerializer):
    """Serializer for uploading/replacing PDF (optional)."""

    class Meta:
        model = Paper
        fields = ["id", "pdf_file"]
        read_only_fields = ["id"]
        extra_kwargs = {"pdf_file": {"required": True}}
