from django.urls import re_path 
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/socket-server/', consumers.ChatConsumer.as_asgi(), kwargs={'model': 'StevenAI'}),
    re_path(r'ws/socket-server-mentor-ai/', consumers.ChatConsumer.as_asgi(), kwargs={'model': 'MentorAI'})
]