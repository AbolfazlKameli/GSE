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

    def create(self, validated_data):
        product = validated_data.get('product')
        quantity = validated_data.get('quantity')
        request = self.context.get('request')

        item_obj = get_cart_item_by_product_id(product_id=product.id, owner_id=request.user.id)
        if item_obj and product.id == item_obj.product.id:
            item_obj.quantity += quantity
            item_obj.save()
            return item_obj

        item_obj = CartItem.objects.create(**validated_data)
        return item_obj
