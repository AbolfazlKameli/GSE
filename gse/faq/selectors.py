from .choices import QUESTION_STATUS_PENDING
from .models import Question, Answer


def get_all_questions() -> list[Question]:
    return Question.objects.all()


def get_question_by_id(question_id: int, status: str = QUESTION_STATUS_PENDING) -> Question | None:
    if status:
        return Question.objects.filter(id=question_id, status=status).first()
    return Question.objects.filter(id=question_id).first()


def get_all_answers() -> list[Answer]:
    return Answer.objects.all()


def get_answer_by_id(answer_id: int) -> Answer | None:
    return Answer.objects.filter(id=answer_id).first()
