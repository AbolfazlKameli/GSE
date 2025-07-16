from urllib.parse import urlencode

from django.conf import settings
from django.core.cache import cache
from django.shortcuts import redirect
from drf_spectacular.utils import extend_schema
from jose.exceptions import JWTError
from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from gse.utils import permissions, format_errors
from gse.utils.doc_serializers import (
    ResponseSerializer,
    TokenResponseSerializer,
    GoogleAuthCallbackSerializer,
    VerificationResponseSerializer
)
from .. import serializers
from ..mixins import ApiErrorsMixin
from ..models import User
from ..selectors import get_user_by_email, is_email_taken
from ..services import (
    register,
    google_get_access_token,
    google_get_user_info,
    update_profile,
    get_authorization_url,
    generate_tokens_for_user,
    generate_access_token,
    decode_token
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


@extend_schema(tags=['Auth'])
class RequestCodeForRegisterAPI(CreateAPIView):
    """
    API for requesting register verification code, accessible only to non-authenticated users,
    """
    serializer_class = serializers.SendVerificationEmailSerializer
    permission_classes = [permissions.NotAuthenticated]

    @extend_schema(responses={202: ResponseSerializer})
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            send_verification_email.delay(
                serializer.validated_data.get('email'),
                content='کد تایید حساب کاربری',
                subject='آسانسور گستران شرق',
                action='verify'
            )
            return Response(
                data={'data': {'message': 'کد فعالسازی به ایمیل شما ارسال شد.'}},
                status=status.HTTP_202_ACCEPTED
            )
        return Response(
            data={'data': {'errors': format_errors(serializer.errors)}},
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(tags=['Auth'])
class UserVerificationAPI(GenericAPIView):
    """
    API for verifying user registration, accessible only to non-authenticated users,
    """
    permission_classes = [permissions.NotAuthenticated]
    http_method_names = ['post', 'head', 'options']
    serializer_class = serializers.UserRegisterVerifySerializer

    @extend_schema(responses={200: VerificationResponseSerializer})
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            access_token = generate_access_token(serializer.validated_data.get('email'), 'verify')
            return Response(
                data={'data': {'message': 'ایمیل با موفقیت اعتبارسنجی شد.', 'access_token': access_token}},
                status=status.HTTP_200_OK
            )
        return Response(
            data={'data': {'errors': format_errors(serializer.errors)}},
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(tags=['Auth'])
class UserRegisterAPI(GenericAPIView):
    """
    API for registering users. takes a JWT token and after verification, registers the user.
    """
    serializer_class = serializers.UserRegisterSerializer
    authentication_classes = []

    @extend_schema(responses={201: ResponseSerializer})
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            token = request.headers.get('Authorization')
            if token is None:
                return Response(
                    data={'data': {'errors': 'ارسال توکن الزامیست.'}},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                payload = decode_token(token[7:])
            except JWTError as e:
                return Response(
                    data={'data': {'errors': str(e)}},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if payload.get('action') != 'verify':
                return Response(
                    data={'data': {'errors': 'ورود غیرمجاز.'}},
                    status=status.HTTP_400_BAD_REQUEST
                )

            email = payload.get('sub')
            if is_email_taken(email):
                return Response(
                    data={'data': {'errors': 'این ایمیل قبلا استفاده شده.'}},
                    status=status.HTTP_400_BAD_REQUEST
                )

            register(email=email, password=serializer.validated_data.get('password'), is_active=True)

            return Response(
                data={'data': {'message': 'حساب کاربری با موفقیت ساخته شد.'}},
                status=status.HTTP_201_CREATED
            )
        return Response(
            data={'data': {'errors': format_errors(serializer.errors)}},
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(tags=['Auth'])
class ResendVerificationEmailAPI(GenericAPIView):
    """
    API for resending a verification email, accessible only to non-authenticated users,
    with a limit of five requests per hour for each IP.
    """
    permission_classes = [permissions.NotAuthenticated]
    serializer_class = serializers.SendVerificationEmailSerializer

    @extend_schema(responses={202: ResponseSerializer})
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user: User | None = get_user_by_email(serializer.validated_data.get('email'))
            response = Response(
                data={'data': {"message": "کد فعالسازی به ایمیل شما ارسال شد."}},
                status=status.HTTP_202_ACCEPTED,
            )
            if user is None:
                return response
            if user.is_active:
                return Response(
                    data={'data': {'message': "این حساب درحال حاضر فعال است."}},
                    status=status.HTTP_400_BAD_REQUEST
                )
            send_verification_email.delay_on_commit(
                email_address=user.email,
                content='کد تایید حساب کاربری',
                subject='آسانسور گستران شرق',
                action='verify'
            )
            return response
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
