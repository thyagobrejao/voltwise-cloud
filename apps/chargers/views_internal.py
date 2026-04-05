"""
Internal API endpoints for service-to-service communication.

These routes are consumed exclusively by voltwise-ocpp and are protected by a
shared API key (X-Internal-Api-Key header), NOT by JWT.

All routes live under /api/internal/ (see chargers/urls.py).
"""

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import IsInternalService

from .ocpp_integration import OCPPIntegrationService


class UpdateChargerStatusView(APIView):
    """
    POST /api/internal/chargers/{identifier}/status/

    Payload: {"status": "available"|"charging"|"offline"|"fault"}
    Called by voltwise-ocpp on BootNotification / StatusNotification.
    """

    permission_classes = [IsInternalService]

    def post(self, request: Request, identifier: str) -> Response:
        new_status = request.data.get("status")
        if not new_status:
            return Response(
                {"detail": "status field is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            charger = OCPPIntegrationService.update_charger_status(identifier, new_status)
        except Exception as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        return Response({"id": str(charger.id), "identifier": charger.identifier, "status": charger.status})


class CreateSessionView(APIView):
    """
    POST /api/internal/sessions/

    Payload: {"charger_identifier": str, "transaction_id": int, "user_tag": str|null}
    Called by voltwise-ocpp on StartTransaction.authorize.
    """

    permission_classes = [IsInternalService]

    def post(self, request: Request) -> Response:
        charger_identifier = request.data.get("charger_identifier")
        transaction_id = request.data.get("transaction_id")

        if not charger_identifier or transaction_id is None:
            return Response(
                {"detail": "charger_identifier and transaction_id are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            session = OCPPIntegrationService.create_session(
                charger_identifier,
                int(transaction_id),
                request.data.get("user_tag"),
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)
        except Exception as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        from apps.sessions.serializers import ChargingSessionSerializer

        return Response(
            ChargingSessionSerializer(session).data,
            status=status.HTTP_201_CREATED,
        )


class StopSessionView(APIView):
    """
    POST /api/internal/sessions/stop/

    Payload: {"transaction_id": int, "energy_kwh": float}
    Called by voltwise-ocpp on StopTransaction.
    """

    permission_classes = [IsInternalService]

    def post(self, request: Request) -> Response:
        transaction_id = request.data.get("transaction_id")
        energy_kwh = request.data.get("energy_kwh", 0.0)

        if transaction_id is None:
            return Response(
                {"detail": "transaction_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            session = OCPPIntegrationService.stop_session(int(transaction_id), float(energy_kwh))
        except Exception as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        from apps.sessions.serializers import ChargingSessionSerializer

        return Response(ChargingSessionSerializer(session).data)


class RecordMeterValueView(APIView):
    """
    POST /api/internal/sessions/meter-values/

    Payload: {"transaction_id": int, "energy_kwh": float}
    Called by voltwise-ocpp on MeterValues (sampled or clock-aligned).
    """

    permission_classes = [IsInternalService]

    def post(self, request: Request) -> Response:
        transaction_id = request.data.get("transaction_id")
        energy_kwh = request.data.get("energy_kwh")

        if transaction_id is None or energy_kwh is None:
            return Response(
                {"detail": "transaction_id and energy_kwh are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        OCPPIntegrationService.record_meter_value(int(transaction_id), float(energy_kwh))
        return Response(status=status.HTTP_204_NO_CONTENT)
