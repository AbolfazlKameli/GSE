from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView, ListAPIView, DestroyAPIView
from rest_framework.response import Response

from gse.utils import format_errors
from gse.utils.doc_serializers import ResponseSerializer
from gse.utils.permissions import IsAdminOrSupporter
from .models import Website
from .selectors import get_all_attributes
from .serializers import WebsiteSerializer


class WebsiteAttributeCreateAPI(GenericAPIView):
    """
    API for creating website attribute, accessible only to admins or supporters.
    """
    serializer_class = WebsiteSerializer
    permission_classes = [IsAdminOrSupporter]

    @extend_schema(responses={201: ResponseSerializer})
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


class WebSiteAttributeListAPI(ListAPIView):
    """
    API for listing website attributes.
    """
    serializer_class = WebsiteSerializer
    queryset = get_all_attributes()


class WebsiteAttributeUpdateAPI(GenericAPIView):
    """
    API for updating an attribute, accessible only to admins and supporters.
    """
    serializer_class = WebsiteSerializer
    permission_classes = [IsAdminOrSupporter]

    @extend_schema(responses={200: ResponseSerializer})
    def patch(self, request, *args, **kwargs):
        attribute = get_object_or_404(Website, id=kwargs.get('attr_id'))
        serializer = self.serializer_class(instance=attribute, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                data={'data': {'message': 'ویژگی به روز رسانی شد.'}},
                status=status.HTTP_200_OK
            )
        return Response(
            data={'data': {'errors': format_errors(serializer.errors)}},
            status=status.HTTP_400_BAD_REQUEST
        )


class WebsiteAttributeDeleteAPI(DestroyAPIView):
    """
    API for deleting attributes, accessible only to admins or supporters.
    """
    serializer_class = WebsiteSerializer
    permission_classes = [IsAdminOrSupporter]
    queryset = get_all_attributes()
    lookup_url_kwarg = 'attr_id'
