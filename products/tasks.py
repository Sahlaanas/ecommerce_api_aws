from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Order

@shared_task
def send_order_confirmation_email(order_id, recipient_email):
    try:
        order = Order.objects.get(id=order_id)
        subject = f'Order Confirmation - #{order.id}'
        message = f'''
        Thank you for your order!
        
        Order Number: {order.id}
        Order Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}
        Order Total: Rs.{order.total_amount}
        
        We are processing your order and will notify you when it ships.
        '''
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,  # Use settings explicitly
            [recipient_email],
            fail_silently=False,  # Ensure it raises an error if email fails
        )
        return f"Order confirmation email sent to : {recipient_email}"
    except Order.DoesNotExist:
        return f"Order {order_id} not found"
    except Exception as e:
        return f"Failed to send email: {str(e)}"
    
