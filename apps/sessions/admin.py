from django.contrib import admin

from .models import ChargingSession


@admin.register(ChargingSession)
class ChargingSessionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "charger",
        "user",
        "status",
        "start_time",
        "end_time",
        "energy_kwh",
        "transaction_id",
    ]
    list_filter = ["status", "charger__organization"]
    search_fields = ["charger__name", "charger__identifier", "user__email"]
    ordering = ["-start_time"]
    date_hierarchy = "start_time"
    readonly_fields = ["created_at", "updated_at"]
    list_select_related = ["charger", "user"]
