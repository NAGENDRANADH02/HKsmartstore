from django.contrib import admin
from .models import Category, Product, ProductImage, ProductVariant

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'vendor', 'price', 'stock', 'is_active')
    inlines = [ProductImageInline, ProductVariantInline]
    prepopulated_fields = {"slug": ("name",)}

admin.site.register(Category)
