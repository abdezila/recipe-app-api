from rest_framework.routers import DefaultRouter
from .views import EventPaperViewSet

router = DefaultRouter()
router.register(
    r"event/(?P<event_id>\d+)/papers",
    EventPaperViewSet,
    basename="event-papers"
)

urlpatterns = router.urls
