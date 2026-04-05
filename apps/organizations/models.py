from django.conf import settings
from django.db import models

from apps.common.models import BaseModel


class Organization(BaseModel):
    """
    Top-level tenant unit.  All chargers and sessions belong to an organization.
    The owner is the user who created it; other users reference it via User.organization.
    """

    name = models.CharField(max_length=255)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_organizations",
    )

    class Meta:
        db_table = "organizations"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name
