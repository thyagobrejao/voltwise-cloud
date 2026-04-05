from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


class RegisterViewTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.url = "/api/auth/register/"

    def test_register_creates_user(self) -> None:
        payload = {
            "name": "Ada Lovelace",
            "email": "ada@example.com",
            "password": "Str0ng@Pass!",
        }
        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertEqual(response.data["email"], payload["email"])
        self.assertNotIn("password", response.data)  # must be write-only

    def test_register_rejects_duplicate_email(self) -> None:
        User.objects.create_user(email="dup@example.com", name="Dup", password="pass123!")
        payload = {
            "name": "Someone Else",
            "email": "dup@example.com",
            "password": "Str0ng@Pass!",
        }
        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_requires_all_fields(self) -> None:
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserModelTest(TestCase):
    def test_create_user_normalises_email(self) -> None:
        user = User.objects.create_user(
            email="TEST@Example.COM", name="Test User", password="P@ssword1"
        )
        self.assertEqual(user.email, "TEST@example.com")

    def test_create_user_stores_hashed_password(self) -> None:
        user = User.objects.create_user(
            email="hash@example.com", name="Hash User", password="P@ssword1"
        )
        self.assertTrue(user.check_password("P@ssword1"))
        self.assertNotEqual(user.password, "P@ssword1")

    def test_create_user_is_active_by_default(self) -> None:
        user = User.objects.create_user(
            email="active@example.com", name="Active", password="P@ssword1"
        )
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)

    def test_create_superuser_sets_flags(self) -> None:
        user = User.objects.create_superuser(
            email="admin@example.com", name="Admin", password="P@ssword1"
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_user_without_email_raises(self) -> None:
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", name="No Email", password="pass")
