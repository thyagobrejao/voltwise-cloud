from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers

from apps.organizations.models import Organization

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
    )
    organization_name = serializers.CharField(
        write_only=True,
        max_length=255,
    )

    class Meta:
        model = User
        fields = ["id", "name", "email", "password", "organization_name"]

    @transaction.atomic
    def create(self, validated_data: dict) -> User:
        organization_name = validated_data.pop("organization_name")
        user = User.objects.create_user(**validated_data)
        org = Organization.objects.create(name=organization_name, owner=user)
        user.organization = org
        user.save(update_fields=["organization", "updated_at"])
        return user


class UserSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(
        source="organization.name",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = User
        fields = ["id", "name", "email", "organization", "organization_name", "created_at"]
        read_only_fields = ["id", "created_at"]
