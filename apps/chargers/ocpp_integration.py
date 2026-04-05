"""
OCPP Integration Service
========================

This module is the boundary between voltwise-ocpp and voltwise-cloud.

voltwise-ocpp (the WebSocket server) calls the internal REST endpoints defined
in ``views_internal.py``.  Those endpoints delegate to this service class,
keeping all business logic in one place and decoupled from HTTP concerns.

Call flow
---------
OCPP message → voltwise-ocpp handler → HTTP POST to /api/internal/... → OCPPIntegrationService

If both services are deployed in the same Python process (e.g. during tests)
the service can be imported and called directly.
"""

import logging
from typing import Optional

from django.utils import timezone

from .models import Charger, ChargerStatus

logger = logging.getLogger(__name__)


# ── WebSocket broadcast helper ────────────────────────────────────────────────

def _ws_broadcast(organization_id, data: dict) -> None:
    """
    Send *data* to every WebSocket client in the organization's channel group.
    Silently ignored when channels / Redis are not available (e.g. unit tests).
    """
    try:
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer

        channel_layer = get_channel_layer()
        if channel_layer is None:
            return
        async_to_sync(channel_layer.group_send)(
            f"org-{organization_id}",
            {"type": "dashboard.event", "data": data},
        )
    except Exception as exc:
        logger.warning("WS broadcast failed: %s", exc)


def _serialize_session(session) -> dict:
    """Return a plain dict for a ChargingSession suitable for WS events."""
    duration = None
    if session.end_time and session.start_time:
        duration = int((session.end_time - session.start_time).total_seconds())
    return {
        "id": str(session.id),
        "charger": str(session.charger_id),
        "charger_name": session.charger.name,
        "charger_identifier": session.charger.identifier,
        "transaction_id": session.transaction_id,
        "start_time": session.start_time.isoformat(),
        "end_time": session.end_time.isoformat() if session.end_time else None,
        "duration_seconds": duration,
        "energy_kwh": str(session.energy_kwh),
        "status": session.status,
    }


class OCPPIntegrationService:
    # ── Charger ───────────────────────────────────────────────────────────────

    @staticmethod
    def update_charger_status(identifier: str, status: str) -> Charger:
        """
        Called on BootNotification / StatusNotification from voltwise-ocpp.
        Updates the charger's operational status.

        Raises ``Charger.DoesNotExist`` if the identifier is unknown.
        """
        charger = Charger.objects.get(identifier=identifier)
        charger.status = status
        charger.save(update_fields=["status", "updated_at"])
        logger.info("Charger %s → %s", identifier, status)

        _ws_broadcast(charger.organization_id, {
            "event": "charger.status",
            "id": str(charger.id),
            "identifier": charger.identifier,
            "status": charger.status,
            "updated_at": charger.updated_at.isoformat(),
        })

        return charger

    # ── Sessions ──────────────────────────────────────────────────────────────

    @staticmethod
    def create_session(
        charger_identifier: str,
        transaction_id: int,
        user_tag: Optional[str] = None,
    ):
        """
        Called on StartTransaction from voltwise-ocpp.
        Creates a new ChargingSession.

        Enforces the rule: only one active session per charger.
        """
        # Deferred import to avoid circular dependency at module load time.
        from apps.sessions.models import ChargingSession, SessionStatus

        charger = Charger.objects.get(identifier=charger_identifier)

        if ChargingSession.objects.filter(charger=charger, status=SessionStatus.ACTIVE).exists():
            raise ValueError(f"Charger {charger_identifier} already has an active session.")

        session = ChargingSession.objects.create(
            charger=charger,
            transaction_id=transaction_id,
            start_time=timezone.now(),
            status=SessionStatus.ACTIVE,
        )
        # Mark charger as charging.
        charger.status = ChargerStatus.CHARGING
        charger.save(update_fields=["status", "updated_at"])

        logger.info("Session %s started on charger %s", session.id, charger_identifier)

        # Broadcast charger status change + new session to portal clients.
        _ws_broadcast(charger.organization_id, {
            "event": "charger.status",
            "id": str(charger.id),
            "identifier": charger.identifier,
            "status": charger.status,
            "updated_at": charger.updated_at.isoformat(),
        })
        session.charger = charger  # ensure relation is cached for serialization
        _ws_broadcast(charger.organization_id, {
            "event": "session.started",
            "session": _serialize_session(session),
        })

        return session

    @staticmethod
    def stop_session(transaction_id: int, energy_kwh: float) -> object:
        """
        Called on StopTransaction from voltwise-ocpp.
        Marks the session as completed and records the final energy reading.
        """
        from apps.sessions.models import ChargingSession, SessionStatus

        session = ChargingSession.objects.select_related("charger").get(
            transaction_id=transaction_id
        )
        session.end_time = timezone.now()
        session.energy_kwh = energy_kwh
        session.status = SessionStatus.COMPLETED
        session.save(update_fields=["end_time", "energy_kwh", "status", "updated_at"])

        # Mark charger back to available.
        session.charger.status = ChargerStatus.AVAILABLE
        session.charger.save(update_fields=["status", "updated_at"])

        logger.info("Session %s completed — %.3f kWh", session.id, energy_kwh)

        # Broadcast.
        _ws_broadcast(session.charger.organization_id, {
            "event": "charger.status",
            "id": str(session.charger.id),
            "identifier": session.charger.identifier,
            "status": session.charger.status,
            "updated_at": session.charger.updated_at.isoformat(),
        })
        _ws_broadcast(session.charger.organization_id, {
            "event": "session.stopped",
            "session": _serialize_session(session),
        })

        return session

    @staticmethod
    def record_meter_value(transaction_id: int, energy_kwh: float) -> Optional[object]:
        """
        Called on MeterValues from voltwise-ocpp.
        Updates the running energy counter on the active session.
        """
        from apps.sessions.models import ChargingSession

        try:
            session = ChargingSession.objects.get(transaction_id=transaction_id)
        except ChargingSession.DoesNotExist:
            logger.warning("MeterValues for unknown transaction_id %s — ignored", transaction_id)
            return None

        session.energy_kwh = energy_kwh
        session.save(update_fields=["energy_kwh", "updated_at"])

        _ws_broadcast(session.charger.organization_id, {
            "event": "session.meter",
            "session_id": str(session.id),
            "transaction_id": session.transaction_id,
            "energy_kwh": str(session.energy_kwh),
        })

        return session
