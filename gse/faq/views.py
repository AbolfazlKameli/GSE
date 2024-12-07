from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from gse.products.models import Product
from gse.utils.format_errors import format_errors
from .selectors import get_all_questions
from .serializers import QuestionSerializer


class QuestionListAPI(ListAPIView):
    """
    API for listing questions, accessible only to admin users.
    """
    serializer_class = QuestionSerializer
    permission_classes = [IsAdminUser]
    queryset = get_all_questions()


class QuestionCreateAPI(GenericAPIView):
    """
    API for creating questions, accessible only to authenticated users.
    """
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        product: Product = get_object_or_404(Product, id=self.kwargs.get('product_id'))
        if serializer.is_valid():
            serializer.save(owner=request.user, product=product)
            return Response(
                data={'data': {'message': 'سوال با موفقیت ایجاد شد.'}},
                status=status.HTTP_201_CREATED
            )
        return Response(
            data={'data': {'errors': format_errors(serializer.errors)}}
        )
