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

def create_admin_user(**params):
    """Create and return admin user."""
    return get_user_model().objects.create_superuser(**params)

class PublicEventAPITests(TestCase):
    """Test unauthenticated API requests."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email = 'user@example.com', password = 'pass123')

    def test_public_can_list_events(self):
        """Test public can list events"""
        res = self.client.get(EVENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_public_can_view_event_detail(self):
        """Test user see detail of events."""
        event = create_event(user = self.user)

        url  = detail_url(event.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_auth_required_to_create_event(self):
        """Test to required authenticate user."""
        payload = {
            'title':'Sample event',
            'location':'ainsmara',
            'start_date':date(2025,12,30),
            'description': 'This is a description', 
            'end_date': date(2025, 12, 31),
        }
        res = self.client.post(EVENTS_URL, payload)

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

    def test_get_event_detail(self):
        """Test get event detail."""
        event = create_event(user = self.user)

        url  = detail_url(event.id)
        res = self.client.get(url)

        serializer = EventDetailSerializer(event)
        self.assertEqual(res.data, serializer.data)

    def test_user_cannot_create_event(self):
        """Authenticated non-admin user cannot create events."""
        payload = {
            'title':'Sample event',
            'location':'ainsmara',
            'start_date':date(2025,12,30),
            'description': 'This is a description', 
            'end_date': date(2025, 12, 31),
        }

        res = self.client.post(EVENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_update_event(self):
        """Authenticated non-admin user cannot update event."""
        event = create_event(user = self.user)
        payload = {'title': 'Hacked title'}

        url = detail_url(event.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_delete_event(self):
        """Authenticated non-admin user cannot delete event."""
        event = create_event(user = self.user)

        url = detail_url(event.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
    
class AdminEventAPITests(TestCase):
    """Test for admin user"""
    def setUp(self):
        self.client = APIClient()
        self.admin_user = create_admin_user(
            email = 'admin@example.com',
            password = 'admin123',
        )
        self.client.force_authenticate(self.admin_user)

    def test_admin_create_event(self):
        """Test admin can create an event"""
        payload = {
            'title': 'Admin Event',
            'location': 'AinSmara',
            'start_date': '2025-12-30',
            'description': 'Created by admin',
            'end_date': '2025-12-31',
            'topics': [{'name': 'AI'}, {'name': 'Cybersecurity'}],  # Add topics to the payload
        }

        res = self.client.post(EVENTS_URL, payload)
        print(res.data)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)


    def test_admin_can_partial_update_event(self):
        """Admin can partially update an event."""
        event = create_event(user=self.admin_user)
        payload = {'title': 'Updated by admin'}

        url = detail_url(event.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        event.refresh_from_db()
        self.assertEqual(event.title, payload['title'])

    def test_admin_can_full_update_event(self):
        """Test admin can fully update an event."""
        event = create_event(user=self.admin_user)
        payload = {
            'title': 'Updated Event',
            'location': 'New Location',
            'start_date': '2025-12-30',
            'description': 'Updated by admin',
            'end_date': '2025-12-31',
            'topics': [{'name': 'AI'}, {'name': 'Cybersecurity'}],
        }

        url = detail_url(event.id)
        res = self.client.put(url, payload)
        print(res.data)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
