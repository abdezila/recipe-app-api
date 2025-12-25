"""Serializers for event APIs"""
from rest_framework import serializers
from core.models import (Event,
                         Topic,
                         EventRegistration,)

REGISTRATION_PRICES = {
    "general": 15000,
    "student": 8000,
    "workshop": 25000,
}

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

class EventRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for event registration"""
    class Meta:
        model = EventRegistration
        fields = [
            "id",
            "user",
            "event",
            "plan",
            "price",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "event",
            "price",
            "created_at",
        ]

    def validate_plan(self, value):
        REGISTRATION_PRICES = {
            "general": 15000,
            "student": 8000,
            "workshop": 25000,
        }
        if value not in REGISTRATION_PRICES:
            raise serializers.ValidationError("Invalid plan.")
        return value

    def create(self, validated_data):
        request = self.context["request"]
        event = self.context["event"]

        if EventRegistration.objects.filter(user=request.user, event=event).exists():
            raise serializers.ValidationError("Already registered.")

        price = {
            "general": 15000,
            "student": 8000,
            "workshop": 25000,
        }[validated_data["plan"]]

        return EventRegistration.objects.create(
            user=request.user,
            event=event,
            plan=validated_data["plan"],
            price=price,
        )

