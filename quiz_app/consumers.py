# consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import CompetitionEntry, Topic, UserTopicScore
from django.shortcuts import get_object_or_404
from asgiref.sync import sync_to_async


def data(entries, scores):

    contestants_data = []
    for entry in entries:
        contestant_username = entry.user.username
        score = next((s.score for s in scores if s.user == entry.user), 0)
        contestants_data.append({"username": contestant_username, "score": score})

    return contestants_data  # Fetching usernames from related User objects


class CompetitionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.topic_id = self.scope["url_route"]["kwargs"]["topic_id"]
        self.group_name = f"competition_{self.topic_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def receive(self, text_data=None):
        # Receive message from WebSocket
        await self.update_contestants(text_data)
        
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def update_contestants(self, event):
        # Send updated contestants list to client
        topic = await sync_to_async(get_object_or_404)(Topic, id=self.topic_id)
        entries = await sync_to_async(list)(CompetitionEntry.objects.filter(topic=topic))
        scores = await sync_to_async(list)(UserTopicScore.objects.filter(topic=topic))
        contestants_data = await sync_to_async(data)(entries, scores)
        await self.send(text_data=json.dumps(contestants_data))