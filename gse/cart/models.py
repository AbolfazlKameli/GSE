from django.db import models

from gse.users.models import User


class Cart(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart')
    created_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
