from django.contrib import admin

from .models import Charger, Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ["name", "organization", "latitude", "longitude", "created_at"]
    list_filter = ["organization"]
    search_fields = ["name"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Charger)
class ChargerAdmin(admin.ModelAdmin):
    list_display = ["name", "identifier", "status", "organization", "location", "created_at"]
    list_filter = ["status", "organization"]
    search_fields = ["name", "identifier"]
    ordering = ["organization", "name"]
    readonly_fields = ["created_at", "updated_at"]
    list_select_related = ["organization", "location"]
