from rest_framework import serializers

from gse.products.serializers import ProductListSerializer
from .models import Cart, CartItem
from .selectors import get_cart_item_by_product_id


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)

    class Meta:
        model = CartItem
        exclude = ('cart',)


class CartSerializer(serializers.ModelSerializer):
    owner = serializers.SlugRelatedField(read_only=True, slug_field='email')
    items = CartItemSerializer(many=True)
    total_price = serializers.SerializerMethodField(read_only=True)

    def get_total_price(self, obj) -> int:
        return obj.get_total_price()

    class Meta:
        model = Cart
        fields = '__all__'


class CartItemAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        exclude = ('cart',)

    def validate(self, attrs):
        product = attrs.get('product')
        quantity = attrs.get('quantity')
        request = self.context.get('request')

        if quantity > product.quantity:
            raise serializers.ValidationError({'quantity': 'این تعداد از این محصول در انبار موجود نمیباشد.'})

        item_obj = get_cart_item_by_product_id(product_id=product.id, owner_id=request.user.id)
        if item_obj and product.id == item_obj.product.id:
            item_obj.quantity += quantity
            if product.quantity < item_obj.quantity:
                raise serializers.ValidationError({'quantity': 'این تعداد از این محصول در انبار موجود نمیباشد.'})

        return attrs


class CartItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ('quantity',)

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError({'quantity': 'این فیلد نمیتواند خالی باشد.'})

        product = self.context.get('product')
        quantity = attrs.get('quantity')
        request = self.context.get('request')

        if quantity > product.quantity:
            raise serializers.ValidationError({'quantity': 'این تعداد از این محصول در انبار موجود نمیباشد.'})

        item_obj = get_cart_item_by_product_id(product_id=product.id, owner_id=request.user.id)
        if item_obj and product.id == item_obj.product.id:
            item_obj.quantity += quantity
            if product.quantity < item_obj.quantity:
                raise serializers.ValidationError({'quantity': 'این تعداد از این محصول در انبار موجود نمیباشد.'})

        return attrs

    def update(self, instance, validated_data):
        quantity = validated_data.get('quantity')
        instance.quantity += quantity
        instance.save()
        return instance
