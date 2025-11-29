from urllib.parse import urlencode

from django.conf import settings
from django.core.cache import cache
from django.shortcuts import redirect
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from gse.utils import permissions, format_errors
from gse.utils.doc_serializers import (
    ResponseSerializer,
    TokenResponseSerializer,
    GoogleAuthCallbackSerializer
)
from .. import serializers
from ..mixins import ApiErrorsMixin
from ..models import User
from ..selectors import get_user_by_email, is_email_taken, get_user_by_phone_number
from ..services import (
    register,
    google_get_access_token,
    google_get_user_info,
    update_profile,
    get_authorization_url,
    generate_tokens_for_user,
    check_otp_code,
    activate_user
)
from ..tasks import send_verification_email


@extend_schema(tags=['Auth'])
class CustomTokenRefreshAPI(TokenRefreshView):
    """
    Custom API for refreshing JWT tokens.
    """


@extend_schema(responses={200: TokenResponseSerializer}, tags=['Auth'])
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom API for obtaining JWT tokens.
    """
    serializer_class = serializers.MyTokenObtainPairSerializer


@extend_schema(tags=["Auth"])
class UserRegisterAPI(GenericAPIView):
    permission_classes = [permissions.NotAuthenticated]
    serializer_class = serializers.SendVerificationEmailSerializer

    @extend_schema(responses={200: ResponseSerializer})
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email")

            if is_email_taken(email):
                return Response(
                    data={"data": {"errors": {"email": "در حال حاضر حساب کاربری با این ایمیل وجود دارد."}}},
                    status=status.HTTP_400_BAD_REQUEST
                )

            send_verification_email.delay(
                email_address=email,
                content="کد تایید حساب کاربری",
                subject="آسآنسور گستران شرق",
            )

            return Response(
                data={"message": "کد فعالسازی با موفقیت به ایمیل شما ارسال شد."},
                status=status.HTTP_200_OK
            )
        return Response(
            data={'data': {'errors': format_errors(serializer.errors)}},
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(tags=["Auth"])
class UserRegisterVerifyAPI(GenericAPIView):
    permission_classes = [permissions.NotAuthenticated]
    serializer_class = serializers.UserRegisterVerifySerializer

    @extend_schema(responses={201: ResponseSerializer})
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            otp_code = serializer.validated_data.get("otp_code")
            password = serializer.validated_data.get("password")

            if not check_otp_code(otp_code=otp_code, email=email):
                return Response(
                    data={"data": {"errors": {"otp_code": "کد وارد شده نامعتبر است."}}},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user = get_user_by_email(email=email)

            if user is not None and not user.is_active:
                activate_user(user)
                return Response(
                    data={'data': {'message': 'کاربر با موفقیت اعتبارسنجی شد.'}},
                    status=status.HTTP_200_OK
                )

            register(email=email, password=password, is_active=True)
            return Response(
                data={"data": {"message": "ایمیل با موفقیت اعتبار سنجی و حساب کاربری ایجاد شد."}},
                status=status.HTTP_201_CREATED
            )
        return Response(
            data={'data': {'errors': format_errors(serializer.errors)}},
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(tags=["Auth"])
class UserVerificationAPI(GenericAPIView):
    permission_classes = [permissions.NotAuthenticated]
    serializer_class = serializers.UserVerificationSerializer

    @extend_schema(responses={202: ResponseSerializer})
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            phone_number = serializer.validated_data.get("phone_number")
            otp_code = serializer.validated_data.get("otp_code")

            if not check_otp_code(otp_code=otp_code, email=email, phone_number=phone_number):
                return Response(
                    data={"data": {"errors": {"otp_code": "کد وارد شده نامعتبر است."}}},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user = get_user_by_email(email=email) if email else get_user_by_phone_number(phone_number=phone_number)
            activate_user(user)

            return Response(
                data={"data": {"message": "حساب کاربری با موفقیت فعال شد."}},
                status=status.HTTP_202_ACCEPTED
            )
        return Response(
            data={'data': {'errors': format_errors(serializer.errors)}},
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(tags=['Auth'])
class GoogleLoginRedirectAPI(GenericAPIView):
    """
    API for redirecting the user to the Google consent screen for authentication,
    accessible only to non-authenticated users.
    """
    permission_classes = [permissions.NotAuthenticated]

    def get(self, request, *args, **kwargs):
        authorization_url, state = get_authorization_url()
        cache.set(f'state_{state}', state, timeout=600)
        return redirect(authorization_url)


@extend_schema(tags=['Auth'])
class GoogleLoginApi(ApiErrorsMixin, GenericAPIView):
    """
    API for handling the Google OAuth2.0 callback after successful authentication,
    accessible for authenticated or new users.
    """
    serializer_class = serializers.GoogleLoginSerializer

    @extend_schema(
        parameters=[
            serializer_class
        ],
        responses={
            200: GoogleAuthCallbackSerializer
        }
    )
    def get(self, request, *args, **kwargs):
        input_serializer = self.serializer_class(data=request.GET)
        input_serializer.is_valid(raise_exception=True)
        validated_data = input_serializer.validated_data

        code = validated_data.get('code')
        error = validated_data.get('error')
        state = validated_data.get('state')

        if error or not code:
            errors = urlencode({'errors': error})
            return Response({'data': {'errors': format_errors(errors)}})

        stored_state = cache.get(f'state_{state}', None)
        if stored_state is None:
            return Response(
                data={'data': {'errors': {'CSRF': 'CSRF check failed.'}}},
                status=status.HTTP_400_BAD_REQUEST
            )

        cache.delete(f'state_{stored_state}')

        redirect_uri = f'{settings.BASE_FRONTEND_URL}'
        access_token = google_get_access_token(code=code, redirect_uri=redirect_uri)
        user_data = google_get_user_info(access_token=access_token)

        user: User | None = get_user_by_email(user_data['email'])
        if user is None:
            user: User = register(email=user_data['email'], is_active=True)
            profile_data = {
                'first_name': user_data['given_name'],
                'last_name': user_data['family_name']
            }
            update_profile(user=user, profile_data=profile_data)

        access_token, refresh_token = generate_tokens_for_user(user)
        response_data = {
            'user': serializers.UserSerializer(user).data,
            'access_token': str(access_token),
            'refresh_token': str(refresh_token)
        }
        return Response(response_data, status=status.HTTP_200_OK)
