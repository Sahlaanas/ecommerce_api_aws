from rest_framework import serializers
from .models import Category, Product, ProductImage, Cart, CartItem, Coupon
from users.serializers import UserSerializer


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'title', 'slug', 'description', 'parent')

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'image', 'is_primary')

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=Category.objects.all(), source='categories'
    )
    
    class Meta:
        model = Product
        fields = ('id', 'title', 'slug', 'description', 'price', 'stock', 
                  'categories', 'category_ids', 'images', 'created_at', 
                  'updated_at', 'is_active')
        
#==================================CART SECTION====================================================================

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.UUIDField(write_only=True)
    subtotal = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_id', 'quantity', 'subtotal')
    
    def get_subtotal(self, obj):
        return obj.quantity * obj.product.price

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    user = UserSerializer
    total = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ('id', 'items', 'total', 'created_at', 'updated_at','user')
    
    def get_total(self, obj):
        return sum(item.quantity * item.product.price for item in obj.items.all())
    
    
#===========================ORDER SECTION==========================================================================

from rest_framework import serializers
from .models import Order, OrderItem
from products.serializers import ProductSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'product_price', 'quantity')

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ('id', 'user', 'status', 'total_amount', 'shipping_address', 
                  'created_at', 'updated_at', 'tracking_number', 'items')
        
#=========================================DISCOUNT & COUPON========================================================


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ('id', 'code', 'description', 'discount_percent', 'is_active',
                  'valid_from', 'valid_to', 'min_purchase_amount', 'max_discount_amount',
                  'usage_limit', 'usage_count')