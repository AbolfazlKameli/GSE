from rest_framework import serializers

from gse.products.serializers import ProductListSerializer
from .models import Cart, CartItem
from .selectors import get_cart_item_by_product_id


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, obj) -> int:
        return obj.get_total_price()

    class Meta:
        model = CartItem
        exclude = ('cart',)


class CartSerializer(serializers.ModelSerializer):
    owner = serializers.SlugRelatedField(read_only=True, slug_field='email')
    items = CartItemSerializer(many=True)
    total_price = serializers.SerializerMethodField(read_only=True)
    total_quantity = serializers.SerializerMethodField(read_only=True)

    def get_total_price(self, obj) -> int:
        return obj.get_total_price()

    def get_total_quantity(self, obj) -> int:
        return obj.get_total_quantity()

    class Meta:
        model = Cart
        fields = '__all__'


class CartItemAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ('quantity', 'product')
        extra_kwargs = {
            'quantity': {'required': True}
        }

    def validate(self, attrs):
        product = attrs.get('product')
        quantity = attrs.get('quantity')
        request = self.context.get('request')

        if not product.available:
            raise serializers.ValidationError({'product': 'محصول موجود نمیباشد.'})

        if quantity > product.quantity or (not quantity > 0):
            raise serializers.ValidationError({'quantity': 'این تعداد از این محصول در انبار موجود نمیباشد.'})

        if (quantity + request.user.cart.get_total_quantity()) > 100:
            raise serializers.ValidationError(
                {'quantity': 'در یک سبد تعدا محصولات نمیتواند بیشتر از ۱۰۰ باشد.'}
            )

        item_obj = get_cart_item_by_product_id(product_id=product.id, owner_id=request.user.id)
        if item_obj:
            item_obj.quantity += quantity

            if product.quantity < item_obj.quantity or (not item_obj.quantity > 0):
                raise serializers.ValidationError({'quantity': 'این تعداد از این محصول در انبار موجود نمیباشد.'})

            if item_obj.quantity > 100:
                raise serializers.ValidationError({'quantity': 'شما نمیتوانید تعدادی بیشتر از ۱۰۰ انتخاب کنید.'})

        return attrs
