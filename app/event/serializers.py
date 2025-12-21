"""Serializers for event APIs"""
from rest_framework import serializers
from core.models import Event, Topic

class TopicSerializer(serializers.ModelSerializer):
    """Serializer for Topics"""
    class Meta:
        model= Topic
        fields = ['id', 'name']
        read_only_fields = ['id']
class EventSerializer(serializers.ModelSerializer):
    """Serializer for events"""
    class Meta:
        model = Event
        fields = ['id', 'title', 'location', 'start_date', 'end_date']
        read_only_fields = ['id']
class EventDetailSerializer(serializers.ModelSerializer):
    """Serializer for event detail view."""
    class Meta(EventSerializer.Meta):
        fields = EventSerializer.Meta.fields + ['description']