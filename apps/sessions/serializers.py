from rest_framework import serializers

from .models import ChargingSession


class ChargingSessionSerializer(serializers.ModelSerializer):
    charger_name = serializers.CharField(source="charger.name", read_only=True)
    charger_identifier = serializers.CharField(source="charger.identifier", read_only=True)
    duration_seconds = serializers.SerializerMethodField()

    class Meta:
        model = ChargingSession
        fields = [
            "id",
            "charger",
            "charger_name",
            "charger_identifier",
            "user",
            "transaction_id",
            "start_time",
            "end_time",
            "duration_seconds",
            "energy_kwh",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_duration_seconds(self, obj) -> int | None:
        if obj.end_time and obj.start_time:
            return int((obj.end_time - obj.start_time).total_seconds())
        return None
