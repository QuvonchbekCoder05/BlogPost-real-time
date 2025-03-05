import json
from channels.generic.websocket import AsyncWebsocketConsumer


class PostConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("posts_updates", self.channel_name)
        await self.accept()
        

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("posts_updates", self.channel_name)
 

    async def post_message(self, event):
        """📡 WebSocket orqali yangi post kelishini xabar qilish"""
        
        await self.send(text_data=json.dumps(event))
