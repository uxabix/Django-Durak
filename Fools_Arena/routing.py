from channels.routing import URLRouter
from channels.auth import AuthMiddlewareStack

from chat.routing import websocket_urlpatterns as chat_routes
from game.routing import websocket_urlpatterns as game_routes

websocket_application = AuthMiddlewareStack(
    URLRouter(chat_routes + game_routes)
)
