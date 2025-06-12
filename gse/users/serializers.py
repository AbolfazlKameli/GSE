from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from gse.orders.serializers import OrderListSerializer
from gse.products.serializers import ProductReviewSerializer
from .models import User
from .selectors import get_user_by_email
from .services import check_otp_code
from .validators import validate_iranian_phone_number, validate_postal_code


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
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
    orders = OrderListSerializer(many=True)
    reviews = ProductReviewSerializer(required=False, many=True, read_only=True)

    class Meta:
        model = User
        exclude = ('password', 'is_superuser')
        read_only_fields = (
            'id',
            'last_login',
            'groups',
            'user_permissions',
            'is_active',
            'role',
            'orders',
        )


class UserUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='profile.first_name', required=False)
    last_name = serializers.CharField(source='profile.last_name', required=False)
    phone_number = serializers.CharField(
        source='profile.phone_number',
        required=False,
        validators=[validate_iranian_phone_number]
    )
    address = serializers.CharField(source='address.address', required=False)
    postal_code = serializers.CharField(source='address.postal_code', required=False, validators=[validate_postal_code])

    class Meta:
        model = User
        exclude = (
            'password',
            'is_superuser',
            'id',
            'last_login',
            'groups',
            'user_permissions',
            'role',
            'is_active'
        )

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError('هیچ اطلاعاتی ارسال نشده.')
        if attrs.get('email') and attrs.get('phone_number'):
            raise serializers.ValidationError('شما نمیتوانید همزمان ایمیل و شماره تلفن را تغییر دهید.')
        return attrs

    # Profile validators
    def validate_first_name(self, value):
        if value and len(value) > 50:
            raise serializers.ValidationError('نام نمیتواند بیشتر از ۵۰ نویسه باشد.')
        return value

    def validate_last_name(self, value):
        if value and len(value) > 50:
            raise serializers.ValidationError('نام خانوادگی نمیتواند بیشتر از ۵۰ نویسه باشد.')
        return value


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
            raise serializers.ValidationError('رمز های عبور باید یکسان باشند.')
        try:
            validate_password(data)
        except serializers.ValidationError:
            raise serializers.ValidationError()
        return data


class UserRegisterVerifySerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=50, required=False)
    phone_number = serializers.CharField(max_length=11, validators=[validate_iranian_phone_number], required=False)
    code = serializers.CharField(max_length=5)

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        email = attrs.get('email')
        if phone_number:
            if not check_otp_code(phone_number=phone_number, otp_code=attrs.get('code')):
                raise serializers.ValidationError({'code': 'کد وارد شده نامعتبر است.'})
        elif email:
            if not check_otp_code(email=email, otp_code=attrs.get('code')):
                raise serializers.ValidationError({'code': 'کد وارد شده نامعتبر است.'})
        else:
            raise serializers.ValidationError('وارد کردن ایمیل یا شماره تلفن الزامیست.')
        return attrs


class ResendVerificationEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class GoogleLoginSerializer(serializers.Serializer):
    code = serializers.CharField(required=False)
    error = serializers.CharField(required=False)
    state = serializers.CharField(required=False)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate_old_password(self, old_password):
        user: User = self.context['user']
        if not user.check_password(old_password):
            raise serializers.ValidationError('رمز نادرست است.')
        return old_password

    def validate_confirm_password(self, data):
        new_password = self.initial_data.get('new_password', False)
        if new_password and data and new_password != data:
            raise serializers.ValidationError('رمز های عبور باید یکسان باشند.')
        try:
            validate_password(data)
        except serializers.ValidationError as e:
            raise serializers.ValidationError({'confirm_password': e.messages})
        return data


class SetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, max_length=50)
    code = serializers.CharField(required=True, max_length=5)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        email: str = attrs.get('email')

        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        if (new_password and confirm_password) and (new_password != confirm_password):
            raise serializers.ValidationError({'new_password': 'رمز های عبور باید یکسان باشند.'})
        try:
            validate_password(new_password)
        except serializers.ValidationError as e:
            raise serializers.ValidationError({'new_password': e.messages})

        if not check_otp_code(email=email, otp_code=attrs.get('code')):
            raise serializers.ValidationError({'code': 'کد وارد شده نامعتبر است.'})

        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class TokenSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True, write_only=True)
