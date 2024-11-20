from rest_framework import serializers

from gse.products.serializers import ProductListSerializer
from .models import Cart, CartItem
from .selectors import get_cart_item_by_product_id
from .utils import check_cart_total_quantity


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)

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

            if not check_cart_total_quantity(item_obj.cart):
                raise serializers.ValidationError(
                    {'quantity': 'در یک سبد خرید تعداد محصولات نمیتواند بیشتر از ۱۰۰ باشد.'}
                )

            if product.quantity <= item_obj.quantity:
                raise serializers.ValidationError({'quantity': 'این تعداد از این محصول در انبار موجود نمیباشد.'})

            if item_obj.quantity >= 100:
                raise serializers.ValidationError({'quantity': 'شما نمیتوانید تعدادی بیشتر از ۱۰۰ انتخاب کنید.'})

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

            if not check_cart_total_quantity(item_obj.cart):
                raise serializers.ValidationError(
                    {'quantity': 'در یک سبد خرید تعداد محصولات نمیتواند بیشتر از ۱۰۰ باشد.'}
                )

            if product.quantity <= item_obj.quantity:
                raise serializers.ValidationError({'quantity': 'این تعداد از این محصول در انبار موجود نمیباشد.'})

            if item_obj.quantity >= 100:
                raise serializers.ValidationError({'quantity': 'شما نمیتوانید تعدادی بیشتر از ۱۰۰ انتخاب کنید.'})

        return attrs

    def update(self, instance, validated_data):
        quantity = validated_data.get('quantity')
        instance.quantity += quantity
        instance.save()
        return instance
