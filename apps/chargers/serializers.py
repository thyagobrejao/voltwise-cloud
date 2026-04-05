from rest_framework import serializers

from .models import Charger, ChargerStatus, Location


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["id", "name", "latitude", "longitude", "created_at"]
        read_only_fields = ["id", "created_at"]


class ChargerSerializer(serializers.ModelSerializer):
    location_detail = LocationSerializer(source="location", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Charger
        fields = [
            "id",
            "name",
            "identifier",
            "status",
            "status_display",
            "organization",
            "location",
            "location_detail",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "organization", "created_at", "updated_at"]

    def validate_identifier(self, value: str) -> str:
        qs = Charger.objects.filter(identifier=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "A charger with this identifier already exists."
            )
        return value


class ChargerStatusSerializer(serializers.ModelSerializer):
    """Minimal serializer used by the internal OCPP status update endpoint."""

    class Meta:
        model = Charger
        fields = ["id", "identifier", "status", "updated_at"]
        read_only_fields = ["id", "identifier", "updated_at"]

    def validate_status(self, value: str) -> str:
        valid = {choice[0] for choice in ChargerStatus.choices}
        if value not in valid:
            raise serializers.ValidationError(
                f"Invalid status. Choose from: {', '.join(valid)}"
            )
        return value
