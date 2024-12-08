from rest_framework import serializers

from .models import Ticket, TicketAnswer


class TicketAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketAnswer
        fields = '__all__'
        extra_kwargs = {
            'ticket': {'read_only': True}
        }


class TicketSerializer(serializers.ModelSerializer):
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
