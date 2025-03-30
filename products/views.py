from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from .models import Category, Product, ProductImage, Cart, CartItem, Order, OrderItem, Coupon
from .serializers import CategorySerializer, ProductSerializer, ProductImageSerializer, CartSerializer,CartItemSerializer, OrderSerializer, CouponSerializer
from .permissions import IsAdminOrReadOnly
from .tasks import send_order_confirmation_email
from rest_framework.throttling import UserRateThrottle
from django.conf import settings

class CouponValidationThrottle(UserRateThrottle):
    scope = 'coupon_validation'


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['categories', 'price', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'stock']
    lookup_field = 'slug'
    
    def get_queryset(self):
        cache_key = f'product_{self.request.query_params}'
        queryset = cache.get(cache_key)
        
        if not queryset:
            queryset = super().get_queryset()
            cache.set(cache_key, queryset, settings.CACHE_TTL)  # Cache for 5 minutes
        
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        cache_key = f'product_{instance.pk}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        serializer = self.get_serializer(instance)
        data = serializer.data
        cache.set(cache_key, data, timeout=300)
        
        return Response(data)
    
    @action(detail=False, methods=['get']) 
    def featured(self, request):
        featured = self.get_queryset().filter(is_active=True)[:5]
        serializer = self.get_serializer(featured, many=True)
        return Response(serializer.data)
        
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def upload_image(self, request, slug=None):
        product = self.get_object()
        serializer = ProductImageSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class CartViewSet(viewsets.GenericViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Get or create cart for the authenticated user
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return Cart.objects.filter(id=cart.id)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
    
    def list(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        try:
            product = Product.objects.get(id=request.data.get('product_id'))
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        if product.stock < int(request.data.get('quantity', 1)):
            return Response(
                {"error": "Not enough stock available"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': request.data.get('quantity', 1)}
        )
        
        if not created:
            cart_item.quantity += int(request.data.get('quantity', 1))
            cart_item.save()
        
        serializer = self.get_serializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        cart = Cart.objects.get(user=request.user)
        
        try:
            product = Product.objects.get(id=request.data.get('product_id'))
            cart_item = CartItem.objects.get(cart=cart, product=product)
            
            if 'quantity' in request.data and int(request.data['quantity']) < cart_item.quantity:
                cart_item.quantity -= int(request.data['quantity'])
                cart_item.save()
            else:
                cart_item.delete()
            
            serializer = self.get_serializer(cart)
            return Response(serializer.data)
            
        except (Product.DoesNotExist, CartItem.DoesNotExist):
            return Response(
                {"error": "Item not found in cart"}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def clear(self, request):
        cart = Cart.objects.get(user=request.user)
        cart.items.all().delete()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)
    
    
#============================================ORDER SECTION=========================================================

 

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Order.objects.all()
        return Order.objects.filter(user=user)
    
    def create(self, request, *args, **kwargs):
        user = request.user
        
        try:
            cart = Cart.objects.get(user=user)
            if not cart.items.exists():
                return Response(
                    {"error": "Cannot create order with empty cart"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Calculate total order amount
            total_amount = sum(item.quantity * item.product.price for item in cart.items.all())
            
            # Check stock availability
            for item in cart.items.all():
                if item.product.stock < item.quantity:
                    return Response(
                        {"error": f"Not enough stock for {item.product.title}"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Create the order
            order = Order.objects.create(
                user=user,
                total_amount=total_amount,
                shipping_address=request.data.get('shipping_address', user.address or '')
            )
            
            # Create order items and update product stock
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    product_name=cart_item.product.title,
                    product_price=cart_item.product.price,
                    quantity=cart_item.quantity
                )
                
                # Update product stock
                product = cart_item.product
                product.stock -= cart_item.quantity
                product.save()
            
            # Clear the cart after order is created
            cart.items.all().delete()
            
            # Send confirmation email (Celery task)
            send_order_confirmation_email.delay(order.id, user.email)
            
            serializer = self.get_serializer(order)
            return Response({
                'order': serializer.data,
                'message': "CONFIRMATION MAIL SENT"
            }, status=status.HTTP_201_CREATED)
            
        except Cart.DoesNotExist:
            return Response(
                {"error": "Cart not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'], url_path='update-status')
    def update_status(self, request, pk=None):
        order = self.get_object()
        
        # Only admins can update order status
        if request.user.role != 'admin':
            return Response(
                {"error": "Only administrators can update order status"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        new_status = request.data.get('status')
        if not new_status or new_status not in dict(Order.STATUS_CHOICES):
            return Response(
                {"error": "Invalid status value"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = new_status
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)
        
    
    
#===========================================COUPON & DISCOUNTS=====================================================


class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAdminOrReadOnly]
    
    @action(detail=False, methods=['post'])
    def validate(self, request):
        self.throttle_classes = [CouponValidationThrottle]
        self.check_throttles(request)
        user = request.user
        code = request.data.get('code')
        
        try:
            coupon = Coupon.objects.get(code=code)
            cart = Cart.objects.get(user=user)
            
            # Calculate cart total
            cart_total = sum(item.quantity * item.product.price for item in cart.items.all())
            
            if coupon.is_valid(user, cart_total):
                # Calculate discount amount
                discount_amount = (cart_total * coupon.discount_percent) / 100
                
                # Apply max discount cap if set
                if coupon.max_discount_amount:
                    discount_amount = min(discount_amount, coupon.max_discount_amount)
                
                return Response({
                    'valid': True,
                    'coupon': CouponSerializer(coupon).data,
                    'cart_total':cart_total,
                    'discount_amount': discount_amount,
                    'cart_total_after_discount': cart_total - discount_amount 
                })
            else:
                return Response({
                    'valid': False,
                    'message': 'This coupon is not valid for your order.'
                })
            
        except Coupon.DoesNotExist:
            return Response(
                {'valid': False, 'message': 'Invalid coupon code.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Cart.DoesNotExist:
            return Response(
                {'valid': False, 'message': 'Cart not found.'},
                status=status.HTTP_404_NOT_FOUND
            )