from rest_framework import serializers

from .models import Question, Answer


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(read_only=True)

    class Meta:
        model = Question
        fields = '__all__'
        extra_kwargs = {
            'product': {'read_only': True},
            'owner': {'read_only': True}
        }
