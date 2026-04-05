from django.conf import settings
from rest_framework.permissions import BasePermission


class IsInternalService(BasePermission):
    """
    Permission for service-to-service requests from voltwise-ocpp.

    Clients must include the shared secret in the X-Internal-Api-Key header.
    This key is configured via the INTERNAL_API_KEY environment variable and
    must never be exposed publicly.
    """

    def has_permission(self, request, view) -> bool:
        api_key = request.headers.get("X-Internal-Api-Key", "")
        expected = settings.INTERNAL_API_KEY
        # Constant-time comparison to prevent timing attacks.
        import hmac

        return bool(api_key) and hmac.compare_digest(api_key, expected)


class IsOrganizationMember(BasePermission):
    """Enforces that the authenticated user belongs to an organization."""

    message = "You must belong to an organization to perform this action."

    def has_permission(self, request, view) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.organization_id is not None
        )
