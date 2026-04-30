from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from apps.organizations.models import Organization

from .filters import ChargerFilter
from .models import Charger
from .serializers import ChargerSerializer


class ChargerViewSet(viewsets.ModelViewSet):
    """
    list:    Return all chargers owned by the current user's organization.
    create:  Register a new charger under the current user's organization.
    partial_update: Update a charger's name, location, or status.

    If the user does not belong to an organization yet, one is created
    automatically on the first charger creation (transparent to the user).
    """

    serializer_class = ChargerSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = ChargerFilter
    search_fields = ["name", "identifier"]
    ordering_fields = ["name", "status", "created_at"]
    # Expose GET (list/retrieve), POST, PATCH only — no full PUT or DELETE.
    http_method_names = ["get", "post", "patch", "head", "options"]

    def _ensure_organization(self):
        """Auto-provision a personal organization if the user lacks one."""
        user = self.request.user
        if user.organization_id is None:
            org = Organization.objects.create(
                name=f"{user.name}'s Organization",
                owner=user,
            )
            user.organization = org
            user.save(update_fields=["organization", "updated_at"])
        return user.organization

    def get_queryset(self):
        org = self.request.user.organization
        if org is None:
            return Charger.objects.none()
        return (
            Charger.objects.filter(organization=org)
            .select_related("location", "organization")
        )

    def perform_create(self, serializer) -> None:
        org = self._ensure_organization()
        serializer.save(organization=org)

