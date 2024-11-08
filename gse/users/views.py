from urllib.parse import urlencode

from django.conf import settings
from django.core.cache import cache
from django.shortcuts import redirect
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.views import TokenObtainPairView

from gse.docs.serializers.doc_serializers import (
    ResponseSerializer,
    TokenResponseSerializer,
    GoogleAuthCallbackSerializer
)
from gse.permissions import permissions
from gse.utils import format_errors
from . import serializers
from .mixins import ApiErrorsMixin
from .models import User
from .selectors import get_user_by_email
from .services import (
    register,
    google_get_access_token,
    google_get_user_info,
    update_profile,
    get_authorization_url,
    generate_tokens_for_user,
    update_last_login
)
from .tasks import send_verification_email
from .throttle import FiveRequestPerHourThrottle


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = serializers.MyTokenObtainPairSerializer
    throttle_classes = [FiveRequestPerHourThrottle]

    @extend_schema(responses={200: TokenResponseSerializer})
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            email = request.data.get("email")
            user = update_last_login(email)
            if user is None:
                return Response(
                    data={'data': {'errors': {'email': 'کاربر با این مشخصات یافت نشد'}}},
                    status=status.HTTP_404_NOT_FOUND
                )
        return Response(data={'data': response.data}, status=response.status_code)


class UsersListAPI(ListAPIView):
    """
    Returns list of users.\n
    allowed methods: GET.
    """
    permission_classes = [IsAdminUser, ]
    queryset = User.objects.all().select_related('profile', 'address')
    serializer_class = serializers.UserSerializer
    filterset_fields = ['is_active', 'is_superuser', 'role']
    search_fields = ['email']


class UserRegisterAPI(CreateAPIView):
    """
    Registers a User.\n
    allowed methods: POST.
    """
    model = User
    serializer_class = serializers.UserRegisterSerializer
    permission_classes = [permissions.NotAuthenticated, ]
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
            data={'data': {'errors': format_errors.format_errors(serializer.errors)}},
            status=status.HTTP_400_BAD_REQUEST
        )


class UserRegisterVerifyAPI(APIView):
    """
    Verification view for registration.\n
    allowed methods: GET.
    """
    permission_classes = [permissions.NotAuthenticated, ]
    http_method_names = ['post', 'head', 'options']
    serializer_class = serializers.UserRegisterVerifySerializer
    throttle_classes = [FiveRequestPerHourThrottle]

    @extend_schema(responses={200: ResponseSerializer})
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user: User | None = get_user_by_email(serializer.validated_data.get('email'))
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
            data={'data': {'errors': format_errors.format_errors(serializer.errors)}},
            status=status.HTTP_400_BAD_REQUEST
        )


class ResendVerificationEmailAPI(APIView):
    """
    Generates a new token and sends it via email.
    Allowed methods: POST.
    """
    permission_classes = [permissions.NotAuthenticated, ]
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
                data={'data': {"message": "لینک فعالسازی به ایمیل شما ارسال شد."}},
                status=status.HTTP_202_ACCEPTED,
            )
        return Response(
            data={'data': {'errors': format_errors.format_errors(serializer.errors)}},
            status=status.HTTP_400_BAD_REQUEST
        )


class GoogleLoginRedirectAPI(APIView):
    """
    This endpoint will redirect the user to the google consent screen.
    """

    def get(self, request, *args, **kwargs):
        authorization_url, state = get_authorization_url()
        cache.set(f'state_{state}', state, timeout=600)
        return redirect(authorization_url)


class GoogleLoginApi(ApiErrorsMixin, APIView):
    """
    The endpoint that google redirect the user after successful authentication.
    """
    permission_classes = ()
    authentication_classes = ()
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
            errors = urlencode({'error': error})
            print(error, code)
            return Response({'data': {'errors': format_errors.format_errors(errors)}})

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


class ChangePasswordAPI(APIView):
    """
    Changes a user password.\n
    allowed methods: POST.
    """
    permission_classes = [IsAuthenticated, ]
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
            data={'data': {'errors': format_errors.format_errors(serializer.errors)}},
            status=status.HTTP_400_BAD_REQUEST
        )


class SetPasswordAPI(APIView):
    """
    set user password for reset_password.\n
    allowed methods: POST.
    """
    permission_classes = [AllowAny, ]
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
            data={'data': {'errors': format_errors.format_errors(serializer.errors)}},
            status=status.HTTP_400_BAD_REQUEST
        )


class ResetPasswordAPI(APIView):
    """
    reset user passwrd.\n
    allowed methods: POST.
    """
    permission_classes = [AllowAny, ]
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
            data={'errors': format_errors.format_errors(serializer.errors)},
            status=status.HTTP_400_BAD_REQUEST
        )


class BlockTokenAPI(APIView):
    """
    Blocks a specified refresh token.
    Allowed methods: POST.
    """
    serializer_class = serializers.TokenSerializer
    permission_classes = [AllowAny, ]

    @extend_schema(responses={200: ResponseSerializer})
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                token = RefreshToken(request.data['refresh'])
            except TokenError:
                return Response(
                    data={'data': {'errors': {'refresh': 'توکن ارسالی نامعتبر یا منقضی شده است.'}}},
                    status=status.HTTP_400_BAD_REQUEST
                )
            token.blacklist()
            return Response(
                data={'data': {'message': 'توکن با موفقیت بلاک شد.'}},
                status=status.HTTP_200_OK
            )
        return Response(
            data={'data': {'errors': format_errors.format_errors(serializer.errors)}},
            status=status.HTTP_400_BAD_REQUEST
        )


class UserProfileAPI(RetrieveAPIView):
    serializer_class = serializers.UserSerializer
    lookup_url_kwarg = 'id'
    lookup_field = 'id'
    queryset = User.objects.filter(is_active=True)
    http_method_names = ['get', 'options', 'head']


class UserProfileUpdateAPI(UpdateAPIView):
    permission_classes = [permissions.IsAdminOrOwnerOrReadOnly]
    lookup_field = 'id'
    lookup_url_kwarg = 'id'
    queryset = User.objects.filter(is_active=True).select_related('profile', 'address')
    serializer_class = serializers.UserUpdateSerializer
    http_method_names = ['patch', 'head', 'options']

    @extend_schema(responses={200: ResponseSerializer})
    def patch(self, request, *args, **kwargs):
        user: User = self.get_object()
        serializer = self.get_serializer(instance=user, data=request.data, partial=True)
        if serializer.is_valid():
            email_changed = 'email' in serializer.validated_data
            message = 'اطلاعات شما با موفقیت به روز رسانی شد.'
            if email_changed:
                user.is_active = False
                user.save()
                send_verification_email.delay_on_commit(
                    email_address=serializer.validated_data['email'],
                    content='کد تایید حساب کاربری',
                    subject='آسانسور گستران شرق'
                )
                message += 'و لینک فعالسازی برای آدرس ایمیل جدید شما ارسال شد.'

            serializer.save()

            return Response(
                data={'data': {'message': message}},
                status=status.HTTP_200_OK
            )
        return Response(
            data={'data': {'errors': format_errors.format_errors(serializer.errors)}},
            status=status.HTTP_400_BAD_REQUEST
        )


class DeleteUserAccountAPI(DestroyAPIView):
    permission_classes = [permissions.IsAdminOrOwner]
    lookup_field = 'id'
    lookup_url_kwarg = 'id'
    queryset = User.objects.filter(is_active=True)
