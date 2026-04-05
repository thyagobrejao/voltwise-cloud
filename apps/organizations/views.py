from rest_framework import mixins, permissions, viewsets

from .models import Organization
from .serializers import OrganizationSerializer


class OrganizationViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    list:   Returns the organization(s) the current user has access to.
    create: Creates a new organization and assigns the creator as owner.
    """

    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ["name"]

    def get_queryset(self):
        user = self.request.user
        if user.organization_id:
            return Organization.objects.filter(id=user.organization_id)
        # User has no org yet — show orgs they own so they can manage them.
        return Organization.objects.filter(owner=user)
