"""
WebSocket consumer for real-time charger and session events.

Each authenticated user joins the channel group for their organization:
    ``org-<organization_id>``

Events pushed to the client (JSON):
    {"event": "charger.status",  "id": "...", "identifier": "...", "status": "...", "updated_at": "..."}
    {"event": "session.started", "session": {...}}
    {"event": "session.meter",   "session_id": "...", "transaction_id": N, "energy_kwh": N}
    {"event": "session.stopped", "session": {...}}
"""

import json

from channels.generic.websocket import AsyncWebsocketConsumer


class ChargerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if not user or not getattr(user, "organization_id", None):
            await self.close(code=4001)
            return

        self.group_name = f"org-{user.organization_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # Client messages are not used — server-only push.
    async def receive(self, text_data=None, bytes_data=None):
        pass

    # ── Channel layer handlers ───────────────────────────────────────────────

    async def dashboard_event(self, event):
        """Forward any dashboard event to the connected WebSocket client."""
        await self.send(text_data=json.dumps(event["data"]))
