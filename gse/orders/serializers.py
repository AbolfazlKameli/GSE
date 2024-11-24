from rest_framework import serializers

from gse.products.serializers import ProductListSerializer
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, obj):
        return obj.total_price

    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, obj):
        return obj.total_price

    class Meta:
        model = Order
        fields = '__all__'


class OrderItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        exclude = ('order',)


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True)

    class Meta:
        model = Order
        exclude = ('owner',)

    def validate(self, attrs):
        request = self.context.get('request')
        items = attrs.get('items')

        if not bool(items):
            raise serializers.ValidationError({'items': 'هیچ محصولی در دیتای اسالی وجود ندارد.'})

        for item in attrs.get('items'):
            cart_item = request.user.cart.items.filter(product=item.get('product')).exists()
            if not cart_item:
                raise serializers.ValidationError(
                    {'product': 'تنها محصولات ثبت شده در سبد خرید به سفارش اضافه میشوند.'}
                )
        return attrs

    def create(self, validated_data):
        owner = validated_data.pop('owner')

        order = Order.objects.create(owner=owner)
        order_items = [OrderItem(order=order, **item) for item in validated_data.get('items')]
        OrderItem.objects.bulk_create(order_items)
        order.save()

        return order
