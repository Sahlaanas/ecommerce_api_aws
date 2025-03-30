from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
from .models import Order
from .serializers import OrderSerializer

@receiver(post_save, sender=Order)
def order_status_update(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    serializer = OrderSerializer(instance)
    
    async_to_sync(channel_layer.group_send)(
        f'order_{instance.id}',
        {
            'type': 'order_update',
            'data': serializer.data
        }
    )