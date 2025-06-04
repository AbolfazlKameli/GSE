from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import RetrieveAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.response import Response

from gse.utils import permissions, format_errors
from gse.utils.doc_serializers import ResponseSerializer
from .. import serializers
from ..models import User
from ..services import update_profile
from ..tasks import send_verification_email, send_verification_sms


@extend_schema(tags=['Profile'])
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


@extend_schema(tags=['Profile'])
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
            profile = serializer.validated_data.pop('profile', None)
            address = serializer.validated_data.pop('address', None)
            user_data = serializer.validated_data
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

            update_profile(user=user, user_data=user_data, profile_data=profile, address_data=address)

            return Response(
                data={'data': {'message': message}},
                status=status.HTTP_200_OK
            )
        return Response(
            data={'data': {'errors': format_errors(serializer.errors)}},
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(tags=['Profile'])
class DeleteUserAccountAPI(DestroyAPIView):
    """
    API for deleting the authenticated user's account. Accessible to admins or the user themselves or support.
    """
    permission_classes = [permissions.IsAdminOrOwner]
    queryset = User.objects.filter(is_active=True)
    serializer_class = serializers.UserSerializer

    def get_object(self):
        return self.request.user
