from .models import Question


def get_all_questions() -> list[Question]:
    return Question.objects.all()
