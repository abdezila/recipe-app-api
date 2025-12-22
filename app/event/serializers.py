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
    topics = TopicSerializer(many = True, required = False)
    class Meta:
        model = Event
        fields = ['id', 'title', 'location', 'start_date', 'end_date', 'topics']
        read_only_fields = ['id']

    def _get_or_create_topics(self, topics, event):
        """Handle getting or creating topics as needed"""
        auth_user = self.context['request'].user
        for topic in topics:
            topic_obj, created = Topic.objects.get_or_create(
                user = auth_user,
                **topic
            )
            event.topics.add(topic_obj)

    def create(self, validated_data):
        """Create a new event."""
        topics = validated_data.pop('topics', [])
        event = Event.objects.create(**validated_data)
        self._get_or_create_topics(topics, event)
        return event
    
    def update(self, instance, validated_data):
        """Update an event."""
        topics = validated_data.pop('topics', None)
        if topics is not None:
            instance.topics.clear()
            self._get_or_create_topics(topics, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
class EventDetailSerializer(serializers.ModelSerializer):
    """Serializer for event detail view."""
    class Meta(EventSerializer.Meta):
        fields = EventSerializer.Meta.fields + ['description']