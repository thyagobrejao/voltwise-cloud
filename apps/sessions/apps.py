from django.apps import AppConfig


class SessionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.sessions"
    # "sessions" is already taken by django.contrib.sessions, so we use a
    # distinct label to avoid Django's app-registry collision check.
    label = "charging_sessions"
