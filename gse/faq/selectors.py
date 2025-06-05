from django.shortcuts import get_object_or_404

from .choices import QUESTION_STATUS_PENDING
from .models import Question, Answer
from gse.products.models import Product


def get_all_questions() -> list[Question]:
    return Question.objects.select_related('answer').all()


def get_product_questions(product_id: int) -> list[Question]:
    get_object_or_404(Product, id=product_id)
    return Question.objects.filter(product_id=product_id)


def get_question_by_id(question_id: int, status: str = QUESTION_STATUS_PENDING) -> Question | None:
    if status:
        return Question.objects.filter(id=question_id, status=status).first()
    return Question.objects.filter(id=question_id).first()


def get_all_answers() -> list[Answer]:
    return Answer.objects.all()


def get_answer_by_id(answer_id: int) -> Answer | None:
    return Answer.objects.filter(id=answer_id).first()
