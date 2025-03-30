from django.test import TestCase
from django.core.cache import cache
from django.urls import reverse
from .models import Product

class RedisCacheTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(title="Test Product", price=10.00)
        cache.clear()
        
    def test_product_caching(self):
        # Ensure cache is empty before starting
        cache.clear()
        
        # First access: should hit the database
        response = self.client.get(reverse("products-detail", args=[self.product.slug]))
        self.assertEqual(response.status_code, 200)
        
        # Check if product is now cached
        cached_data = cache.get(f"product_{self.product.id}")
        self.assertIsNotNone(cached_data)  # Ensure cache is populated
        
        # Second access: should hit the cache
        response = self.client.get(reverse("products-detail", args=[self.product.slug]))
        self.assertEqual(response.status_code, 200)
