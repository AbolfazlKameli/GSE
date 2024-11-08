from rest_framework import serializers

from gse.users.serializers import UserSerializer


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


class GoogleAuthCallbackSerializer(serializers.Serializer):
    user = UserSerializer()
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
