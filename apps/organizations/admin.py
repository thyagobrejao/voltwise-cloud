from django.contrib import admin

from .models import Organization


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ["name", "owner", "member_count", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["name", "owner__email"]
    raw_id_fields = ["owner"]
    readonly_fields = ["created_at", "updated_at"]

    @admin.display(description="Members")
    def member_count(self, obj) -> int:
        return obj.members.count()
