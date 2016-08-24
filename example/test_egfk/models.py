from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.db import models

from django_egfk.fields import GenericForeignKey


class Main(models.Model):
    text = models.TextField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)


class Child(models.Model):
    object_id = models.PositiveIntegerField()
    main = models.ForeignKey(Main, related_name="child")
    content_object = GenericForeignKey('main.content_type', 'object_id')
