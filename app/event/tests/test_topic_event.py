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

def create_user(email = 'user@example.com', password = 'testpass123', is_staff = False):
    """Create and return a user."""
    return get_user_model().objects.create_user(email = email, password = password, is_staff = is_staff)

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

class PrivateTopicsApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = create_user(
            email= 'admin@example.com',
            password= 'admin1234',
            is_staff  = True,
        )
        self.client.force_authenticate(self.admin_user)
    
    def test_admin_can_create_topic(self):
        """Create topic by admin."""
        payload = {'name': 'AI'}

        res = self.client.post(TOPICS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Topic.objects.filter(name = 'AI').exists())
 