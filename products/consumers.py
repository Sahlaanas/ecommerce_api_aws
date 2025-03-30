import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Order

class OrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        
        if not self.user.is_authenticated:
            await self.close()
            return
            
        self.order_id = self.scope['url_route']['kwargs']['order_id']
        self.room_group_name = f'order_{self.order_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Check if user has permission to access this order
        if await self.can_access_order(self.user, self.order_id):
            await self.accept()
        else:
            await self.close()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    @database_sync_to_async
    def can_access_order(self, user, order_id):
        try:
            order = Order.objects.get(id=order_id)
            return user.id == order.user.id or user.user_type == 'admin'
        except Order.DoesNotExist:
            return False
    
    # Receive message from WebSocket
    async def receive(self, text_data):
        pass  # Client doesn't send data, just receives updates
    
    # Receive message from room group
    async def order_update(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'order_update',
            'data': event['data']
        }))