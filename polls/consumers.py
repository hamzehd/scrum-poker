import json
from channels.generic.websocket import AsyncWebsocketConsumer


class PollConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.poll_id = self.scope['url_route']['kwargs']['poll_id']
        self.poll_room = f'poll_{self.poll_id}'

        # Join poll group
        await self.channel_layer.group_add(
            self.poll_room,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.poll_room,
            self.channel_name
        )

    async def receive(self, text_data):
        parsed_data = json.loads(text_data)
        action = parsed_data['action']

        await self.channel_layer.group_send(
            self.poll_room,
            {
                'type': 'poll_action',
                'action': action
            }
        )

    async def poll_action(self, event):
        message = event['action']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
