from rest_framework import serializers

from .models import Ticket, TicketAnswer


class TicketAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketAnswer
        fields = '__all__'
        read_only_fields = ('ticket',)


class TicketSerializer(serializers.ModelSerializer):
    answer = TicketAnswerSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = '__all__'
        read_only_fields = ('owner', 'status')


class TicketsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'
