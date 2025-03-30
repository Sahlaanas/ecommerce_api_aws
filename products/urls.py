from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, CartViewSet, OrderViewSet , CouponViewSet # Import the viewsets

# Create a router object
router = DefaultRouter()

# Register ViewSets with the router
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='products')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'order', OrderViewSet, basename='order')
router.register(r'coupons', CouponViewSet, basename='coupon')

# Include the generated URLs from the router
urlpatterns = [
    path('', include(router.urls)),  # Includes all registered viewsets
]