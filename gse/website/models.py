from django.db import models


class Website(models.Model):
    attribute = models.CharField(max_length=255)
    value = models.TextField()
