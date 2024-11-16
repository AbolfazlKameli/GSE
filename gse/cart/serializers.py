from rest_framework import serializers

from .models import Cart


class CartSerializer(serializers.ModelSerializer):
    owner = serializers.SlugRelatedField(read_only=True, slug_field='email')

    class Meta:
        model = Cart
        fields = '__all__'
