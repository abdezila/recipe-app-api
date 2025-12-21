"""URL mapping for the event app"""
from django.urls import (
    path, include
)
from rest_framework.routers import DefaultRouter
from event import views

router = DefaultRouter()
router.register('events', views.EventViewSet)
router.register('topics', views.TopicViewSet)

app_name = 'event'
urlpatterns = [
    path('', include(router.urls))
]
