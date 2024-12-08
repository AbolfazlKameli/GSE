from rest_framework import serializers

from .models import Ticket, TicketAnswer
from .services import submit_answer


class TicketAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketAnswer
        fields = '__all__'
        extra_kwargs = {
            'ticket': {'read_only': True}
        }

    def save(self, **kwargs):
        submit_answer(
            ticket=kwargs.get('ticket'),
            title=self.validated_data.get('title'),
            body=self.validated_data.get('body')
        )


class TicketSerializer(serializers.ModelSerializer):
    answers = TicketAnswerSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = '__all__'
        extra_kwargs = {
            'owner': {'read_only': True},
            'status': {'read_only': True}
        }


class TicketsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'
