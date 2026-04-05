"""
JWT authentication middleware for Django Channels WebSocket connections.

Clients pass the JWT access token as a query-string parameter:

    ws://host/ws/chargers/?token=<access_token>

The middleware resolves the token to a User instance (with organization
pre-loaded) and attaches it to ``scope["user"]`` before the consumer runs.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware

User = get_user_model()


@database_sync_to_async
def _resolve_token(token_str: str):
    """Return the User for *token_str*, or AnonymousUser on any failure."""
    from rest_framework_simplejwt.tokens import AccessToken

    try:
        token = AccessToken(token_str)
        return User.objects.select_related("organization").get(id=token["user_id"])
    except Exception:
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    """Extracts ``?token=`` from the WS query string and resolves it to a user."""

    async def __call__(self, scope, receive, send):
        qs = scope.get("query_string", b"").decode()
        token_str = None
        for part in qs.split("&"):
            if part.startswith("token="):
                token_str = part[6:]
                break

        scope["user"] = await _resolve_token(token_str) if token_str else AnonymousUser()
        return await super().__call__(scope, receive, send)


def JWTAuthMiddlewareStack(inner):
    return JWTAuthMiddleware(inner)
