from urllib.parse import urlencode

from django.conf import settings
from django.core.cache import cache
from django.shortcuts import redirect
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    DestroyAPIView,
    GenericAPIView
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from gse.utils import permissions, format_errors
from gse.utils.doc_serializers import (
    ResponseSerializer,
    TokenResponseSerializer,
    GoogleAuthCallbackSerializer
)
from . import serializers
from .mixins import ApiErrorsMixin
from .models import User
from .selectors import get_user_by_email, get_user_by_phone_number
from .services import (
    register,
    google_get_access_token,
    google_get_user_info,
    update_profile,
    get_authorization_url,
    generate_tokens_for_user
)
from .tasks import send_verification_email, send_verification_sms
from .throttle import FiveRequestPerHourThrottle


@extend_schema(responses={200: TokenResponseSerializer})
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom API for obtaining JWT tokens.
    """
    serializer_class = serializers.MyTokenObtainPairSerializer
    throttle_classes = [FiveRequestPerHourThrottle]


class UsersListAPI(ListAPIView):
    """
    API for listing all users, accessible only to admin users.
    """
    permission_classes = [permissions.IsAdminOrSupporter]
    queryset = User.objects.all().select_related('profile', 'address')
    serializer_class = serializers.UserSerializer
    filterset_fields = ['is_active', 'is_superuser', 'role']
    search_fields = ['email']


class UserRegisterAPI(CreateAPIView):
    """
    API for user registration, accessible only to non-authenticated users,
    with a limit of five requests per hour for each IP.
    """
    model = User
    serializer_class = serializers.UserRegisterSerializer
    permission_classes = [permissions.NotAuthenticated]
    throttle_classes = [FiveRequestPerHourThrottle]

    @extend_schema(responses={201: ResponseSerializer})
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            vd = serializer.validated_data
            register(email=vd['email'], password=vd['password'])
            send_verification_email.delay_on_commit(
                email_address=vd['email'],
                content='کد تایید حساب کاربری',
                subject='آسانسور گستران شرق'
            )
            return Response(
                data={'data': {'message': 'کد فعالسازی به ایمیل شما ارسال شد.'}},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            data={'data': {'errors': format_errors(serializer.errors)}},
            status=status.HTTP_400_BAD_REQUEST
        )


class UserVerificationAPI(GenericAPIView):
    """
    API for verifying user registration, accessible only to non-authenticated users,
    with a limit of five requests per hour for each IP.
    """
    permission_classes = [permissions.NotAuthenticated]
    http_method_names = ['post', 'head', 'options']
    serializer_class = serializers.UserRegisterVerifySerializer
    throttle_classes = [FiveRequestPerHourThrottle]

    @extend_schema(responses={200: ResponseSerializer})
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data.get('phone_number')
            email = serializer.validated_data.get('email')
            user = None
            if phone_number:
                user: User | None = get_user_by_phone_number(phone_number=phone_number)
            elif email:
                user: User | None = get_user_by_email(email=email)
            if user is None:
                return Response(
                    data={'data': {'errors': {'email': 'حساب کاربری با این مشخصات یافت نشد.'}}},
                    status=status.HTTP_404_NOT_FOUND
                )

            if user.is_active:
                return Response(
                    data={'data': {'message': 'این حساب کاربری قبلاً فعال شده است.'}},
                    status=status.HTTP_409_CONFLICT
                )
            user.is_active = True
            user.save()
            return Response(
                data={'data': {'message': 'حساب کاربری با موفقیت فعال شد.'}},
                status=status.HTTP_200_OK
            )
        return Response(
            data={'data': {'errors': format_errors(serializer.errors)}},
            status=status.HTTP_400_BAD_REQUEST
        )


class ResendVerificationEmailAPI(GenericAPIView):
    """
    API for resending a verification email, accessible only to non-authenticated users,
    with a limit of five requests per hour for each IP.
    """
    permission_classes = [permissions.NotAuthenticated]
    serializer_class = serializers.ResendVerificationEmailSerializer
    throttle_classes = [FiveRequestPerHourThrottle]

    @extend_schema(responses={202: ResponseSerializer})
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user: User = serializer.validated_data['user']
            send_verification_email.delay_on_commit(
                email_address=user.email,
                content='کد تایید حساب کاربری',
                subject='آسانسور گستران شرق'
            )
            return Response(
                data={'data': {"message": "کد فعالسازی به ایمیل شما ارسال شد."}},
                status=status.HTTP_202_ACCEPTED,
            )
        return Response(
            data={'data': {'errors': format_errors(serializer.errors)}},
            status=status.HTTP_400_BAD_REQUEST
        )


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
            update_profile(user_id=user.id, profile_data=profile_data)

        access_token, refresh_token = generate_tokens_for_user(user)
        response_data = {
            'user': serializers.UserSerializer(user).data,
            'access_token': str(access_token),
            'refresh_token': str(refresh_token)
        }
        return Response(response_data, status=status.HTTP_200_OK)


class ChangePasswordAPI(GenericAPIView):
    """
    API for changing a user's password, accessible only to the user or an admin or support.
    """
    permission_classes = [permissions.IsAdminOrOwner]
    serializer_class = serializers.ChangePasswordSerializer

    @extend_schema(responses={
        200: ResponseSerializer
    })
    def put(self, request):
        serializer = self.serializer_class(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            user: User = request.user
            new_password = serializer.validated_data['new_password']
            user.set_password(new_password)
            user.save()
            return Response(
                data={'data': {'message': 'رمز شما با موفقیت تغییر کرد.'}},
                status=status.HTTP_200_OK
            )
        return Response(
            data={'data': {'errors': format_errors(serializer.errors)}},
            status=status.HTTP_400_BAD_REQUEST
        )


class SetPasswordAPI(GenericAPIView):
    """
    API for setting a user's password during the reset password process, accessible to all users.
    """
    permission_classes = [AllowAny]
    serializer_class = serializers.SetPasswordSerializer
    throttle_classes = [FiveRequestPerHourThrottle]

    @extend_schema(responses={
        200: ResponseSerializer
    })
    def post(self, request):
        email: str = request.data.get('email')
        user: User | None = get_user_by_email(email)
        if user is None:
            return Response(
                data={'data': {'errors': {'email': 'حساب کاربری با این مشخصات یافت نشد.'}}},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            new_password = serializer.validated_data['new_password']
            user.set_password(new_password)
            user.save()
            return Response(
                data={'data': {'message': 'رمز شما با موفقیت تغییر کرد.'}},
                status=status.HTTP_200_OK
            )
        return Response(
            data={'data': {'errors': format_errors(serializer.errors)}},
            status=status.HTTP_400_BAD_REQUEST
        )


class ResetPasswordAPI(GenericAPIView):
    """
    API for initiating the password reset process by sending a reset link to the user's email, accessible to all users.
    """
    permission_classes = [AllowAny]
    serializer_class = serializers.ResetPasswordSerializer
    throttle_classes = [FiveRequestPerHourThrottle]

    @extend_schema(responses={
        202: ResponseSerializer
    })
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user: User | None = get_user_by_email(serializer.validated_data.get('email'))
            if user is None:
                return Response(
                    data={'data': {'errors': {'email': 'حساب کاربری با این مشخصات یافت نشد.'}}},
                    status=status.HTTP_404_NOT_FOUND
                )

            send_verification_email.delay_on_commit(
                email_address=user.email,
                content='کد فراموشی رمز:',
                subject='آسانسور گستران شرق'
            )

            return Response(
                data={'data': {'message': 'لینک بازنشانی رمز عبور به ایمیل شما ارسال شد.'}},
                status=status.HTTP_202_ACCEPTED
            )
        return Response(
            data={'errors': format_errors(serializer.errors)},
            status=status.HTTP_400_BAD_REQUEST
        )


class UserProfileAPI(RetrieveAPIView):
    """
    API for retrieving the authenticated user's profile information.
    Accessible to admins or the user themselves or support.
    """
    serializer_class = serializers.UserSerializer
    queryset = User.objects.filter(is_active=True)
    permission_classes = [permissions.IsAdminOrOwner]
    http_method_names = ['get', 'options', 'head']

    def get_object(self):
        return self.request.user


class UserProfileUpdateAPI(UpdateAPIView):
    """
    API for updating the authenticated user's profile.
    Includes support for updating email with re-verification if changed.
    Accessible to admins or the user themselves or support.
    """
    permission_classes = [permissions.IsAdminOrOwner]
    queryset = User.objects.filter(is_active=True).select_related('profile', 'address')
    serializer_class = serializers.UserUpdateSerializer
    http_method_names = ['patch', 'head', 'options']

    def get_object(self):
        return self.request.user

    @extend_schema(responses={200: ResponseSerializer})
    def patch(self, request, *args, **kwargs):
        user: User = self.get_object()
        serializer = self.get_serializer(instance=user, data=request.data, partial=True)
        if serializer.is_valid():
            profile = serializer.validated_data.get('profile')
            email_changed = 'email' in serializer.validated_data
            phone_changed = 'phone_number' in profile if profile else False
            message = 'اطلاعات شما با موفقیت به روز رسانی شد.'
            if email_changed or phone_changed:
                user.is_active = False
                user.save()
                if email_changed:
                    send_verification_email.delay_on_commit(
                        email_address=serializer.validated_data['email'],
                        content='کد تایید حساب کاربری',
                        subject='آسانسور گستران شرق'
                    )
                    message += 'و کد فعالسازی برای آدرس ایمیل جدید شما ارسال شد.'

                if phone_changed:
                    send_verification_sms.delay_on_commit(
                        phone_number=serializer.validated_data.get('profile').get('phone_number')
                    )
                    message += 'و کد فعالسازی برای شماره تلفن جدید شما ارسال شد.'

            serializer.save()

            return Response(
                data={'data': {'message': message}},
                status=status.HTTP_200_OK
            )
        return Response(
            data={'data': {'errors': format_errors(serializer.errors)}},
            status=status.HTTP_400_BAD_REQUEST
        )


class DeleteUserAccountAPI(DestroyAPIView):
    """
    API for deleting the authenticated user's account. Accessible to admins or the user themselves or support.
    """
    permission_classes = [permissions.IsAdminOrOwner]
    queryset = User.objects.filter(is_active=True)
    serializer_class = serializers.UserSerializer

    def get_object(self):
        return self.request.user
