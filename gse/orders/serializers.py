from rest_framework import serializers

from gse.payment.serializers import PaymentSerializer
from gse.products.serializers import ProductListSerializer
from .choices import ORDER_STATUS_PENDING
from .models import Order, OrderItem, Coupon
from .selectors import (
    get_usable_coupon_for_update_by_code,
    get_coupon_for_update_by_code,
    check_order_status,
    check_order_owner,
    get_order_for_update_by_id
)


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, obj) -> int:
        return obj.total_price

    class Meta:
        model = OrderItem
        fields = '__all__'


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ('code', 'discount_percent', 'max_usage_limit', 'expiration_date')
        extra_kwargs = {
            'discount_percent': {'required': True},
            'max_usage_limit': {'required': True},
        }


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    payment = PaymentSerializer(read_only=True, many=True)
    total_price = serializers.SerializerMethodField(read_only=True)
    coupon = CouponSerializer(read_only=True)

    def get_total_price(self, obj) -> int:
        return obj.total_price

    class Meta:
        model = Order
        fields = '__all__'


class OrderListSerializer(serializers.ModelSerializer):
    coupon = CouponSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'status', 'discount_percent', 'created_date', 'updated_date', 'owner', 'coupon')


class OrderItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        exclude = ('order',)


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True)

    class Meta:
        model = Order
        fields = ('items',)


class CouponApplySerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50, required=True, write_only=True)
    order_id = serializers.IntegerField(required=True, write_only=True)

    def validate(self, attrs):
        code = attrs.get('code')
        order_id = attrs.get('order_id')
        allowed_statuses = [ORDER_STATUS_PENDING]

        order: Order | None = get_order_for_update_by_id(order_id=order_id)
        if order is None or not check_order_status(order, allowed_statuses) or not check_order_owner(order):
            raise serializers.ValidationError({'order': 'سفارش درحال پردازشی با این مشخصات وجود ندارد.'})
        if order.coupon is not None:
            raise serializers.ValidationError({'order': 'نمیتوان دو کد تخفیف برای یک سفارش اعمال کرد.'})

        coupon_obj: Coupon | None = get_usable_coupon_for_update_by_code(coupon_code=code)
        if coupon_obj is None:
            raise serializers.ValidationError({'code': 'این کد منقضی یا نامعتبر است.'})

        attrs['order'] = order
        return attrs


class CouponDiscardSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50, required=True, write_only=True)
    order_id = serializers.IntegerField(required=True, write_only=True)

    def validate(self, attrs):
        code = attrs.get('code')
        order_id = attrs.get('order_id')
        allowed_statuses = [ORDER_STATUS_PENDING]

        order: Order | None = get_order_for_update_by_id(order_id=order_id)
        if order is None or not check_order_status(order, allowed_statuses) or not check_order_owner(order):
            raise serializers.ValidationError({'order': 'سفارش درحال پردازشی با این مشخصات وجود ندارد.'})
        if order.coupon is None:
            raise serializers.ValidationError({'order': 'کد تخفیفی روی این سفارش اعمال نشده.'})

        coupon_obj: Coupon | None = get_coupon_for_update_by_code(code=code)
        if coupon_obj is None:
            raise serializers.ValidationError({'code': 'عملیات با خطا مواجه شد. دوباره امتحان کنید.'})

        attrs['order'] = order
        return attrs
