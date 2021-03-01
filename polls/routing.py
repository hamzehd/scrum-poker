from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('ws/poll/<uuid:poll_id>/', consumers.PollConsumer.as_asgi()),
]