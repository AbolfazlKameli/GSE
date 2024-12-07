from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import ListAPIView, GenericAPIView, DestroyAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from gse.permissions.permissions import IsAdminOrOwner
from gse.products.models import Product
from gse.utils.db_utils import is_child_of
from gse.utils.format_errors import format_errors
from .models import Question
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


class QuestionDeleteAPI(DestroyAPIView):
    """
    API for deleting questions, accessible only to owner or admin or supporter.
    """
    serializer_class = QuestionSerializer
    permission_classes = [IsAdminOrOwner]
    queryset = get_all_questions()

    def delete(self, request, *args, **kwargs):
        if not is_child_of(Product, Question, kwargs.get('product_id'), kwargs.get('pk')):
            return Response(
                data={'data': {'errors': 'سوال با این مشخصات پیدا نشد.'}},
                status=status.HTTP_404_NOT_FOUND
            )
        question: Question = get_object_or_404(Question, id=kwargs.get('pk'))
        self.check_object_permissions(request, question)
        question.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
