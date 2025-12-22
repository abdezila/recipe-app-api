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
    topics = TopicSerializer(many=True, required=False, write_only=True)
    topics_detail = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id',
            'title',
            'location',
            'start_date',
            'end_date',
            'topics',
            'topics_detail',
        ]
        read_only_fields = ['id']

    def get_topics_detail(self, obj):
        return TopicSerializer(obj.topics.all(), many=True).data

    def _get_or_create_topics(self, topics, event):
        for topic in topics:
            topic_obj, _ = Topic.objects.get_or_create(
                name=topic['name']
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

class EventDetailSerializer(EventSerializer):
    """Serializer for event detail view."""
    class Meta(EventSerializer.Meta):
        fields = EventSerializer.Meta.fields + ['description']
