from django.urls import path

from .consumers import ChargerConsumer

websocket_urlpatterns = [
    path("ws/chargers/", ChargerConsumer.as_asgi()),
]
