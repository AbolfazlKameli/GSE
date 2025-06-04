from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from gse.utils import permissions, format_errors
from gse.utils.doc_serializers import ResponseSerializer
from .. import serializers
from ..models import User
from ..selectors import get_user_by_email
from ..tasks import send_verification_email


@extend_schema(tags=['Users'])
class UsersListAPI(ListAPIView):
    """
    API for listing all users, accessible only to admin users.
    """
    permission_classes = [permissions.IsAdminOrSupporter]
    queryset = User.objects.all().select_related('profile', 'address')
    serializer_class = serializers.UserSerializer
    filterset_fields = ['is_active', 'is_superuser', 'role']
    search_fields = ['email']


@extend_schema(tags=['Users'])
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


@extend_schema(tags=['Users'])
class SetPasswordAPI(GenericAPIView):
    """
    API for setting a user's password during the reset password process, accessible to all users.
    """
    permission_classes = [AllowAny]
    serializer_class = serializers.SetPasswordSerializer

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


@extend_schema(tags=['Users'])
class ResetPasswordAPI(GenericAPIView):
    """
    API for initiating the password reset process by sending a reset link to the user's email, accessible to all users.
    """
    permission_classes = [AllowAny]
    serializer_class = serializers.ResetPasswordSerializer

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
