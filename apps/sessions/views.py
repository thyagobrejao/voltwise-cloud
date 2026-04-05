from rest_framework import mixins, permissions, viewsets

from apps.common.permissions import IsOrganizationMember

from .models import ChargingSession
from .serializers import ChargingSessionSerializer


class ChargingSessionViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    list:     Return all sessions for the current user's organization.
    retrieve: Return a single session by ID.

    Sessions are read-only via the public API.
    Creation and mutation happen through the internal OCPP endpoints.
    """

    serializer_class = ChargingSessionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    filterset_fields = ["status", "charger"]
    search_fields = ["charger__name", "charger__identifier"]
    ordering_fields = ["start_time", "end_time", "energy_kwh", "status"]

    def get_queryset(self):
        return (
            ChargingSession.objects.filter(charger__organization=self.request.user.organization)
            .select_related("charger", "user")
        )
