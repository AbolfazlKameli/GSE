from rest_framework import serializers

from gse.products.serializers import ProductListSerializer
from .models import Cart, CartItem


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
        fields = ('product',)
