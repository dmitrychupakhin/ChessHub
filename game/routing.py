from django.urls import re_path, path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/home/$", consumers.HomeConsumer.as_asgi()),
    re_path(r"ws/game/(?P<game_id>\w+)/$", consumers.GameConsumer.as_asgi()),
    re_path(r"ws/game-connect/(?P<link>[-\w]+)/$", consumers.GameConnectConsumer.as_asgi()),
]