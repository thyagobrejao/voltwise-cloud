from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from apps.chargers.models import Charger
from apps.organizations.models import Organization
from apps.sessions.models import ChargingSession, SessionStatus

User = get_user_model()


class ChargingSessionModelTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="driver@example.com", name="Driver", password="P@ssword1"
        )
        self.org = Organization.objects.create(name="Acme EV", owner=self.user)
        self.charger = Charger.objects.create(
            name="Charger A", identifier="CP-001", organization=self.org
        )

    def test_end_time_must_be_after_start_time(self) -> None:
        now = timezone.now()
        session = ChargingSession(
            charger=self.charger,
            start_time=now,
            end_time=now - timedelta(hours=1),
            status=SessionStatus.COMPLETED,
        )
        with self.assertRaises(ValidationError):
            session.clean()

    def test_valid_session_passes_clean(self) -> None:
        now = timezone.now()
        session = ChargingSession(
            charger=self.charger,
            start_time=now,
            end_time=now + timedelta(hours=1),
            status=SessionStatus.COMPLETED,
        )
        # Should not raise.
        session.clean()

    def test_active_session_has_no_end_time(self) -> None:
        now = timezone.now()
        session = ChargingSession.objects.create(
            charger=self.charger,
            start_time=now,
            status=SessionStatus.ACTIVE,
        )
        self.assertIsNone(session.end_time)
        self.assertEqual(session.status, SessionStatus.ACTIVE)
