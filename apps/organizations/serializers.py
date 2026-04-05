from rest_framework import serializers

from .models import Organization


class OrganizationSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source="owner.email", read_only=True)
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = ["id", "name", "owner", "owner_email", "member_count", "created_at"]
        read_only_fields = ["id", "owner", "created_at"]

    def get_member_count(self, obj) -> int:
        return obj.members.count()

    def create(self, validated_data: dict) -> Organization:
        user = self.context["request"].user
        validated_data["owner"] = user
        org = super().create(validated_data)

        # Associate the creator with their new organization.
        user.organization = org
        user.save(update_fields=["organization", "updated_at"])
        return org
