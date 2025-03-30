from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage, Cart, CartItem, Order, OrderItem, Coupon

class ProductImageInline(admin.StackedInline):  # Using StackedInline for vertical layout
    model = ProductImage
    extra = 1  # Allows adding images inline

class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'stock', 'is_active', 'created_at', 'stacked_images')
    search_fields = ('title', 'description')
    list_filter = ('is_active', 'categories')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ProductImageInline]  # Attach ProductImage as a stacked inline inside ProductAdmin

    def stacked_images(self, obj):
        images = obj.images.all()[:3]  # Show up to 3 images stacked
        if images:
            return format_html("<br>".join(
                f'<img src="{image.image.url}" width="50" style="border-radius:5px; margin-bottom:5px;" />'
                for image in images
            ))
        return "(No Images)"

    stacked_images.short_description = "Images"

admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)  
admin.site.register(Coupon)
