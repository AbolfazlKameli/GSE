from django.core.exceptions import ValidationError
from rest_framework import serializers

from gse.payment.serializers import PaymentSerializer
from gse.products.serializers import ProductListSerializer
from .choices import ORDER_STATUS_PENDING
from .models import Order, OrderItem, Coupon
from .selectors import get_usable_coupon_by_code, get_order_by_id, get_coupon_by_code, check_order_status
from .services import apply_coupon, discard_coupon, create_order


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
        order = create_order(owner, validated_data.get('items'))
        return order


class CouponApplySerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50, required=True, write_only=True)
    order_id = serializers.IntegerField(required=True, write_only=True)

    def validate(self, attrs):
        code = attrs.get('code')
        order_id = attrs.get('order_id')
        allowed_statuses = [ORDER_STATUS_PENDING]

        order: Order | None = get_order_by_id(order_id=order_id, check_owner=False)
        if order is None or not check_order_status(order, allowed_statuses):
            raise serializers.ValidationError({'order': 'سفارش درحال پردازشی با این مشخصات وجود ندارد.'})
        if order.coupon is not None:
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


class CouponDiscardSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50, required=True, write_only=True)
    order_id = serializers.IntegerField(required=True, write_only=True)

    def validate(self, attrs):
        code = attrs.get('code')
        order_id = attrs.get('order_id')
        allowed_statuses = [ORDER_STATUS_PENDING]

        order: Order | None = get_order_by_id(order_id=order_id, check_owner=False)
        if order is None or not check_order_status(order, allowed_statuses):
            raise serializers.ValidationError({'order': 'سفارش درحال پردازشی با این مشخصات وجود ندارد.'})
        if order.coupon is None:
            raise serializers.ValidationError({'order': 'کد تخفیفی روی این سفارش اعمال نشده.'})

        coupon_obj: Coupon | None = get_coupon_by_code(code=code)
        if coupon_obj is None:
            raise serializers.ValidationError({'code': 'عملیات با خطا مواجه شد. دوباره امتحان کنید.'})

        attrs['order'] = order
        return attrs

    def save(self, *args, **kwargs):
        coupon: Coupon | None = get_coupon_by_code(code=self.validated_data.get('code'))
        order: Order = self.validated_data.get('order')

        try:
            discard_coupon(order, coupon)
        except Exception:
            raise serializers.ValidationError({'data': {'errors': {'order': 'عملیات با شکست مواجه شد.'}}})
