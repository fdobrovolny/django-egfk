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


"""
 Multiple GenericForeignKey TestCase
A (egfk)-> B (D ContentType HERE)
^
| (fk)
C(D ID HERE) (egfk)-> D
"""


class A(models.Model):
    content_type_B = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    object_id_B = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type_B', 'object_id_B')


class B(models.Model):
    content_type_D = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)


class C(models.Model):
    A = models.ForeignKey(A)
    object_id_D = models.PositiveIntegerField(blank=True, null=True)
    content_object_D = GenericForeignKey('A.content_object.content_type_D', 'object_id_D')


class D(models.Model):
    text = models.TextField()
