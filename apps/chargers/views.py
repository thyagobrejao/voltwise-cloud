from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from apps.common.permissions import IsOrganizationMember

from .filters import ChargerFilter
from .models import Charger
from .serializers import ChargerSerializer


class ChargerViewSet(viewsets.ModelViewSet):
    """
    list:    Return all chargers owned by the current user's organization.
    create:  Register a new charger under the current user's organization.
    partial_update: Update a charger's name, location, or status.
    """

    serializer_class = ChargerSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    filterset_class = ChargerFilter
    search_fields = ["name", "identifier"]
    ordering_fields = ["name", "status", "created_at"]
    # Expose GET (list/retrieve), POST, PATCH only — no full PUT or DELETE.
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        return (
            Charger.objects.filter(organization=self.request.user.organization)
            .select_related("location", "organization")
        )

    def perform_create(self, serializer) -> None:
        serializer.save(organization=self.request.user.organization)
