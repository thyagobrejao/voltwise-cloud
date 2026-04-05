from django.db import models

from apps.common.models import BaseModel


class ChargerStatus(models.TextChoices):
    AVAILABLE = "available", "Available"
    CHARGING = "charging", "Charging"
    OFFLINE = "offline", "Offline"
    FAULT = "fault", "Fault"


class Location(BaseModel):
    """Physical location that can group one or more chargers (e.g. a hotel car park)."""

    name = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="locations",
    )

    class Meta:
        db_table = "locations"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Charger(BaseModel):
    """
    Represents a physical EV charging point.

    ``identifier`` is the OCPP charge-point identity string used to route
    messages from voltwise-ocpp to this record.
    """

    name = models.CharField(max_length=255)
    identifier = models.CharField(max_length=100, unique=True, db_index=True)
    status = models.CharField(
        max_length=20,
        choices=ChargerStatus.choices,
        default=ChargerStatus.OFFLINE,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="chargers",
    )
    location = models.ForeignKey(
        Location,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="chargers",
    )

    class Meta:
        db_table = "chargers"
        ordering = ["organization", "name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.identifier})"
