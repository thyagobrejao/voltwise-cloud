from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.common.models import BaseModel


class SessionStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"


class ChargingSession(BaseModel):
    """
    Represents a single EV charging transaction.

    ``transaction_id`` mirrors the OCPP transactionId so voltwise-ocpp can
    reference the session without knowing its internal UUID.
    """

    charger = models.ForeignKey(
        "chargers.Charger",
        on_delete=models.PROTECT,
        related_name="sessions",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="sessions",
    )

    # OCPP transaction identifier — set when the session is opened via StartTransaction.
    transaction_id = models.IntegerField(null=True, blank=True, db_index=True)

    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    energy_kwh = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    status = models.CharField(
        max_length=20,
        choices=SessionStatus.choices,
        default=SessionStatus.ACTIVE,
    )

    class Meta:
        db_table = "charging_sessions"
        ordering = ["-start_time"]
        constraints = [
            # Enforce unique transaction IDs when set.
            models.UniqueConstraint(
                fields=["transaction_id"],
                condition=models.Q(transaction_id__isnull=False),
                name="unique_transaction_id",
            )
        ]

    def __str__(self) -> str:
        return f"Session {self.id} [{self.status}]"

    def clean(self) -> None:
        if self.end_time and self.start_time and self.end_time <= self.start_time:
            raise ValidationError({"end_time": "end_time must be after start_time."})
