"""Tetes for topic api."""
#from datetime import date
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient
from core.models import Event,Topic
from event.serializers import (EventSerializer,
                               EventDetailSerializer,
                               TopicSerializer,)

TOPICS_URL = reverse('event:topic-list')

def create_user(email = 'user@example.com', password = 'testpass123'):
    """Create and return a user."""
    return get_user_model().objects.create_user(email = email, password = password)

def create_admin_user(email = 'admin@example.com', password = 'admin123'):
    """Create and return a admin user."""
    return get_user_model().objects.create_superuser(email= email, password= password)


def detail_url(topic_id):
    """Create and return specific url."""
    return reverse('event:topic-detail', args= [ topic_id])

class PublicTopicsApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_topics(self):
        """Test retrieving a list of topics."""
        Topic.objects.create(name = 'AI')
        Topic.objects.create(name = 'Cybersecurity')

        res = self.client.get(TOPICS_URL)
        topics = Topic.objects.all().order_by('-name')
        serializer = TopicSerializer(topics, many = True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_public_cannot_create_topic(self):
        """Test for user cant create topics."""
        payload = {'name':'Blockchain'}

        res = self.client.post(TOPICS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

class AdminTopicApiTests(TestCase):
    """Test admin CRUD actions for topics."""
    
    def setUp(self):
        self.client = APIClient()
        self.admin_user = create_admin_user()
        self.client.force_authenticate(self.admin_user)

    def test_admin_can_update_topic(self):
        topic = Topic.objects.create(name='AI')
        payload = {'name': 'Artificial Intelligence'}
        url = reverse('event:topic-detail', args=[topic.id])
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        topic.refresh_from_db()
        self.assertEqual(topic.name, payload['name'])

    def test_admin_can_delete_topic(self):
        topic = Topic.objects.create(name='AI')
        url = detail_url(topic.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Topic.objects.filter(id=topic.id).exists())
