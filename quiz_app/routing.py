# routing.py

from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/competition/<str:topic_id>/', consumers.CompetitionConsumer.as_asgi()),
]
