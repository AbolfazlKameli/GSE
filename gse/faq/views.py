from django.http import Http404
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView, GenericAPIView, DestroyAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from gse.products.models import Product
from gse.utils import is_child_of, format_errors
from gse.utils.doc_serializers import ResponseSerializer
from gse.utils.permissions import IsAdminOrOwner, IsAdminOrSupporter
from .models import Question, Answer
from .selectors import get_all_questions, get_all_answers, get_question_by_id, get_answer_by_id, get_product_questions
from .serializers import QuestionSerializer, AnswerSerializer
from .services import remove_answer


class QuestionListAPI(ListAPIView):
    """
    API for listing questions, accessible only to admin users.
    """
    serializer_class = QuestionSerializer
    permission_classes = [IsAdminOrSupporter]
    queryset = get_all_questions()
    filterset_fields = ['status']


class ProductQuestionListAPI(ListAPIView):
    """
    API for listing question by product id.
    """
    serializer_class = QuestionSerializer
    filterset_fields = ['status']

    def get_queryset(self):
        return get_product_questions(self.kwargs.get('product_id'))


class QuestionRetrieveAPI(RetrieveAPIView):
    """
    API for retrieving question.
    """
    serializer_class = QuestionSerializer
    queryset = get_all_questions()
    lookup_url_kwarg = 'question_id'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return Response(
            data={'data': response.data},
            status=response.status_code
        )


class QuestionCreateAPI(GenericAPIView):
    """
    API for creating questions, accessible only to authenticated users.
    """
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={201: ResponseSerializer})
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
    lookup_url_kwarg = 'question_id'


class AnswerCreateAPI(GenericAPIView):
    """
    API for creating answers, accessible only to admin users.
    """
    serializer_class = AnswerSerializer
    permission_classes = [IsAdminOrSupporter]

    def get_object(self):
        question: Question | None = get_question_by_id(question_id=self.kwargs.get('question_id'))
        if question:
            return question
        raise Http404('سوال بدون پاسخی با این شناسه نشد.')

    @extend_schema(responses={201: ResponseSerializer})
    def post(self, request, *args, **kwargs):
        question: Question = self.get_object()
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(question=question)
            return Response(
                data={'data': {'message': 'پاسخ با موفقیت ثبت شد.'}},
                status=status.HTTP_201_CREATED
            )
        return Response(
            data={'data': {'errors': format_errors(serializer.errors)}},
            status=status.HTTP_400_BAD_REQUEST
        )


class AnswerDeleteAPI(DestroyAPIView):
    """
    API for deleting answers, accessible only to admin users.
    """
    serializer_class = AnswerSerializer
    queryset = get_all_answers()
    permission_classes = [IsAdminOrSupporter]

    def get_object(self):
        if not is_child_of(
                parent_type=Question,
                child_type=Answer,
                parent_id=self.kwargs.get('question_id'),
                child_id=self.kwargs.get('answer_id')
        ):
            raise Http404('پاسخ مرتبط با این سوال پیدا نشد.')
        answer: Answer = get_answer_by_id(self.kwargs.get('answer_id'))
        return answer

    def delete(self, request, *args, **kwargs):
        question: Question = get_object_or_404(Question, id=kwargs.get('question_id'))
        remove_answer(question, self.get_object())
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
