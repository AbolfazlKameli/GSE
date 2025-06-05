from rest_framework import serializers

from .models import Question, Answer


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'
        extra_kwargs = {
            'question': {'read_only': True}
        }


class QuestionSerializer(serializers.ModelSerializer):
    answer = AnswerSerializer(read_only=True)

    class Meta:
        model = Question
        fields = '__all__'
        read_only_fields = ('product', 'owner', 'status')
