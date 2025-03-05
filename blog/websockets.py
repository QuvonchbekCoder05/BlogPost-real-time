from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .serializers import PostSerializer
import json


def send_post_update(action, post):
    """📡 WebSocket orqali postni real vaqtda yangilash"""
    channel_layer = get_channel_layer()
    data = {
        "type": "post_message",
        "action": action,
        "post": PostSerializer(post).data,
    }
   
    async_to_sync(channel_layer.group_send)("posts_updates", data)
