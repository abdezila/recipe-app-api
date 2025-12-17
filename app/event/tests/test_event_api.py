"""Test for event apis."""
from datetime import date
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient
from core.models import Event
from event.serializers import (EventSerializer,
                               EventDetailSerializer,)

EVENTS_URL = reverse('event:event-list')
def detail_url(event_id):
    """Create and return a event detail URL."""
    return reverse('event:event-detail', args= [event_id])

def create_event(user, **params):
    """Create and return a simple event."""
    defaults = {
        'title': 'Sample event title',
        'description': 'good one bro',
        'location': 'AinSmara',
        'start_date': date(2025,12,12),
        'end_date': date(2025,12,31),
    }
    defaults.update(params)

    event = Event.objects.create(user = user, **defaults)
    return event

def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)

class PublicEventAPITests(TestCase):
    """Test unauthenticated API requests."""
    
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API"""
        res = self.client.get(EVENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateEventAPITests(TestCase):
    """Test authenticated API request."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email = 'user@example.com', password = 'test123')
        self.client.force_authenticate(self.user)

    def test_retrieve_events(self):
        """Test returieving a list of events."""
        create_event(user = self.user)
        create_event(user = self.user)

        res = self.client.get(EVENTS_URL)

        events = Event.objects.all().order_by('-id')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        serializer = EventSerializer(events, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_event_list_limited_to_user(self):
        """Test list of events is limited to authenticated user."""
        other_user = create_user(email = 'other@example.com', password = 'password123')
        create_event(user = other_user)
        create_event(user = other_user)

        res = self.client.get(EVENTS_URL)

        events = Event.objects.filter(user = self.user)
        serializer = EventSerializer(events, many = True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """Test get event detail."""
        event = create_event(user = self.user)

        url  = detail_url(event.id)
        res = self.client.get(url)

        serializer = EventDetailSerializer(event)
        self.assertEqual(res.data, serializer.data)

    def test_create_event(self):
        """Test creating a event."""
        payload = {
            'title':'Sample event',
            'location':'ainsmara',
            'start_date':date(2025,12,30),
            'description': 'This is a description', 
            'end_date': date(2025, 12, 31),
        }
        res = self.client.post(EVENTS_URL, payload)
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        event = Event.objects.get(id = res.data['id'])
        for k,v in payload.items():
            self.assertEqual(getattr(event,k), v)
        self.assertEqual(event.user, self.user)

    def test_partial_update(self):
        """Test partial update of a event."""
        event = create_event(
            user = self.user,
            title = 'Sample title',
            location = 'ainsmara',
            description = 'wwoow bro',
            start_date = date(2025,12,30),
            end_date = date(2025, 12, 31),
        )
        payload = {'title':'New event title'}
        url = detail_url(event.id)
        res =self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        event.refresh_from_db()
        self.assertEqual(event.title, payload['title'])
        self.assertEqual(event.user, self.user)

    def test_full_update(self):
        """Test full update of event."""
        event = create_event(
            user = self.user,
            title = 'Sample title',
            location = 'ainsmara',
            description = 'wwoow bro',
            start_date = date(2025,12,30),
            end_date = date(2025, 12, 31),
        )

        payload = {
            'title' : 'Sample title',
            'location' : 'ainsmara',
            'description' : 'wwoow bro',
            'start_date' : date(2025,12,30),
            'end_date' : date(2025, 12, 31),
        }

        url = detail_url(event.id)
        res = self.client.put(url , payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        event.refresh_from_db()
        for k,v in payload.items():
            self.assertEqual(getattr(event,k), v)
        self.assertEqual(event.user, self.user)

    def test_delete_event(self):
        """Test deleting a event successful."""
        event = create_event(user = self.user)

        url = detail_url(event.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Event.objects.filter(id=event.id).exists())