from django.contrib import admin

from .models import Product, ProductCategory, ProductDetail, ProductMedia


class ProductDetailInline(admin.TabularInline):
    model = ProductDetail
    fields = ('attribute', 'value')


class ProductMediaInline(admin.TabularInline):
    model = ProductMedia
    fields = ('media_type', 'media_url', 'is_primary')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'id', 'unit_price', 'available', 'quantity')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}
    inlines = (ProductDetailInline, ProductMediaInline)


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'id', 'is_sub')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}


@admin.register(ProductDetail)
class ProductDetailAdmin(admin.ModelAdmin):
    list_display = ('product__id', 'attribute', 'value')


@admin.register(ProductMedia)
class ProductMediaAdmin(admin.ModelAdmin):
    list_display = ('product', 'media_type', 'media_url')
