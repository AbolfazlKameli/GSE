from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from gse.permissions.permissions import IsAdminOrSupporter
from gse.utils.format_errors import format_errors
from gse.website.serializers import WebsiteSerializer


class WebsiteAttributeCreateAPI(GenericAPIView):
    """
    API for creating website attribute.
    """
    serializer_class = WebsiteSerializer
    permission_classes = [IsAdminOrSupporter]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                data={'data': {'message': 'ویژگی وبسایت با موفقیت ایحاد و ثبت شد.'}},
                status=status.HTTP_201_CREATED
            )
        return Response(
            data={'data': {'errors': format_errors(serializer.errors)}},
            status=status.HTTP_400_BAD_REQUEST
        )
