from .models import Question, Answer
from django.db import transaction

from .choices import QUESTION_STATUS_ANSWERED, QUESTION_STATUS_PENDING


@transaction.atomic
def submit_answer(question: Question, body) -> Answer:
    answer: Answer = Answer.objects.create(
        body=body,
        question=question
    )
    question.status = QUESTION_STATUS_ANSWERED
    question.save()
    return answer


@transaction.atomic
def remove_answer(question: Question, answer: Answer) -> Question:
    answer.delete()
    question.status = QUESTION_STATUS_PENDING
    question.save()
    return question
