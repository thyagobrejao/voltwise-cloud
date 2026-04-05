from rest_framework.routers import DefaultRouter

from .views import ChargingSessionViewSet

router = DefaultRouter()
router.register("sessions", ChargingSessionViewSet, basename="session")

urlpatterns = router.urls
