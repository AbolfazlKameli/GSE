from rest_framework import serializers


class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()


class ResponseSerializer(serializers.Serializer):
    data = MessageSerializer()


class UserInfoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.CharField()


class MyTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()
    user = UserInfoSerializer()


class TokenResponseSerializer(serializers.Serializer):
    data = MyTokenSerializer()
