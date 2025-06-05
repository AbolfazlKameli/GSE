from rest_framework import serializers

from .models import Question, Answer
from .services import submit_answer


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'
        extra_kwargs = {
            'question': {'read_only': True}
        }

    def save(self, **kwargs):
        submit_answer(question=kwargs.get('question'), body=self.validated_data.get('body'))


class QuestionSerializer(serializers.ModelSerializer):
    answer = AnswerSerializer(read_only=True)

    class Meta:
        model = Question
        fields = '__all__'
        read_only_fields = ('product', 'owner', 'status')
