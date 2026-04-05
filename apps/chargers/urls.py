from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ChargerViewSet
from .views_internal import (
    CreateSessionView,
    RecordMeterValueView,
    StopSessionView,
    UpdateChargerStatusView,
)

router = DefaultRouter()
router.register("chargers", ChargerViewSet, basename="charger")

urlpatterns = router.urls + [
    # ── Internal endpoints (voltwise-ocpp → voltwise-cloud) ──────────────────
    path(
        "internal/chargers/<str:identifier>/status/",
        UpdateChargerStatusView.as_view(),
        name="internal-charger-status",
    ),
    path(
        "internal/sessions/",
        CreateSessionView.as_view(),
        name="internal-session-create",
    ),
    path(
        "internal/sessions/stop/",
        StopSessionView.as_view(),
        name="internal-session-stop",
    ),
    path(
        "internal/sessions/meter-values/",
        RecordMeterValueView.as_view(),
        name="internal-meter-values",
    ),
]
