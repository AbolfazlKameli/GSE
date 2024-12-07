from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser

from .selectors import get_all_questions
from .serializers import QuestionSerializer


class QuestionListAPI(ListAPIView):
    """
    API for listing questions, accessible only to admin users.
    """
    serializer_class = QuestionSerializer
    permission_classes = [IsAdminUser]
    queryset = get_all_questions()
