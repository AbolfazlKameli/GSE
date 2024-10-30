from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user, lifetime=None):
        token = super().get_token(user)
        if lifetime:
            token.set_exp(claim='exp', lifetime=lifetime)
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data.update({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': self.user.id,
                'email': self.user.email
            }
        })
        return data


class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='profile.first_name', required=False)
    last_name = serializers.CharField(source='profile.last_name', required=False)
    phone_number = serializers.CharField(source='profile.phone_number', required=False)
    address = serializers.CharField(source='address.address', required=False)
    postal_code = serializers.CharField(source='address.postal_code', required=False)

    class Meta:
        model = User
        exclude = ('password', 'is_superuser')
        read_only_fields = (
            'id',
            'last_login',
            'groups',
            'user_permissions',
            'is_active',
            'role'
        )

    def update(self, instance, validated_data):
        # fetching objects data
        profile_data = validated_data.pop('profile', {})
        user_data = validated_data

        # saving user profile info
        profile = instance.profile
        profile.save()

        # saving user info
        instance.email = user_data.get('email', instance.email)
        instance.save()

        return instance

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError('fields can not be blank.')
        return attrs

    def validate_email(self, email):
        users = User.objects.filter(email__exact=email)
        if users.exists():
            raise serializers.ValidationError('user with this Email already exists.')
        return email


class UserRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(required=True, write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('email', 'password', 'password2')
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 8},
        }

    def validate_password2(self, data):
        password1 = self.initial_data.get('password', False)
        if password1 and data and password1 != data:
            raise serializers.ValidationError('Passwords must match.')
        try:
            validate_password(data)
        except serializers.ValidationError:
            raise serializers.ValidationError()
        return data


class ResendVerificationEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('User does not exist!')
        if user.is_active:
            raise serializers.ValidationError('Account already active!')
        attrs['user'] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate_old_password(self, old_password):
        user: User = self.context['user']
        if not user.check_password(old_password):
            raise serializers.ValidationError('Your old password is not correct.')
        return old_password

    def validate_confirm_password(self, data):
        new_password = self.initial_data.get('new_password', False)
        if new_password and data and new_password != data:
            raise serializers.ValidationError('Passwords must match.')
        try:
            validate_password(data)
        except serializers.ValidationError as e:
            raise serializers.ValidationError({'confirm_password': e.messages})
        return data


class SetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        if new_password and confirm_password and new_password != confirm_password:
            raise serializers.ValidationError({'new_password': 'Passwords must match.'})
        try:
            validate_password(new_password)
        except serializers.ValidationError as e:
            raise serializers.ValidationError({'new_password': e.messages})
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class TokenSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True, write_only=True)
