from django.db import models

from gse.products.models import Product
from gse.users.models import User
from .choices import QUESTION_STATUS_CHOICES, QUESTION_STATUS_PENDING


class Question(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='questions')
    body = models.CharField(max_length=255)
    status = models.CharField(choices=QUESTION_STATUS_CHOICES, default=QUESTION_STATUS_PENDING, max_length=10)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_date',)


class Answer(models.Model):
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='answers')
    body = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_date',)
