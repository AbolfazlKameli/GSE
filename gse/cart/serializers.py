from rest_framework import serializers

from gse.products.serializers import ProductListSerializer
from .models import Cart, CartItem


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
