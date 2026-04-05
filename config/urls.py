from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Public API
    path("api/", include("apps.users.urls")),
    path("api/", include("apps.organizations.urls")),
    path("api/", include("apps.chargers.urls")),
    path("api/", include("apps.sessions.urls")),
]
