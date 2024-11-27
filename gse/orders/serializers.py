from django.core.exceptions import ValidationError
from rest_framework import serializers

from gse.products.serializers import ProductListSerializer
from .models import Order, OrderItem, Coupon
from .selectors import get_usable_coupon_by_code, get_order_by_id
from .services import apply_coupon


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


class OrderListSerializer(serializers.ModelSerializer):
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

        for item in items:
            cart_item = request.user.cart.items.filter(product=item.get('product'))
            if not cart_item.exists():
                raise serializers.ValidationError(
                    {'product': 'تنها محصولات ثبت شده در سبد خرید به سفارش اضافه میشوند.'}
                )
            if item.get('quantity') != cart_item.first().quantity:
                raise serializers.ValidationError(
                    {'quantity': 'تعداد باید با تعداد ثبت شده در سبد خرید یکسان باشد.'}
                )
        return attrs

    def create(self, validated_data):
        owner = validated_data.pop('owner')

        order = Order.objects.create(owner=owner)
        order_items = [OrderItem(order=order, **item) for item in validated_data.get('items')]
        OrderItem.objects.bulk_create(order_items)
        order.save()

        return order


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ('code', 'discount_percent', 'max_usage_limit', 'expiration_date')
        extra_kwargs = {
            'discount_percent': {'required': True},
            'max_usage_limit': {'required': True},
        }


class CouponApplySerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50, required=True, write_only=True)
    order_id = serializers.IntegerField(required=True, write_only=True)

    def validate(self, attrs):
        code = attrs.get('code')
        order_id = attrs.get('order_id')

        order: Order | None = get_order_by_id(order_id=order_id)
        if order is None:
            raise serializers.ValidationError({'order': 'سفارش درحال پردازشی با این مشخصات وجود ندارد.'})
        if order.coupon_applied:
            raise serializers.ValidationError({'order': 'نمیتوان دو کد تخفیف برای یک سفارش اعمال کرد.'})

        coupon_obj: Coupon | None = get_usable_coupon_by_code(coupon_code=code)
        if coupon_obj is None:
            raise serializers.ValidationError({'code': 'این کد منقضی یا نامعتبر است.'})

        attrs['order'] = order
        return attrs

    def save(self, **kwargs):
        coupon: Coupon | None = get_usable_coupon_by_code(coupon_code=self.validated_data.get('code'))
        order: Order = self.validated_data.get('order')
        try:
            apply_coupon(order, coupon)
        except ValidationError:
            raise serializers.ValidationError({'data': {'errors': {'order': 'درصد تخفیف نمیتواند بیشتر از ۱۰۰ باشد.'}}})
