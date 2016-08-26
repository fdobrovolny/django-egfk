from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.db import models

from django_egfk.fields import EnhancedGenericForeignKey


class TestSampleModel(models.Model):
    """You can use this model to test GenericForeignKey."""
    text = models.TextField()

"""
Basic GenericForeignKey on another model connected via ForeignKey.
Child (object_id) -(fk) > Main(content_type)
  |
(egfk)
  V
Some Model
"""


class Main(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)


class Child(models.Model):
    object_id = models.PositiveIntegerField()
    main = models.ForeignKey(Main, related_name="child")
    content_object = EnhancedGenericForeignKey('main.content_type', 'object_id')


"""
Multiple nestead GenericForeignKey TestCase
A (egfk)-> B (D ContentType HERE)
^
| (fk)
C(D ID HERE) (egfk)-> D(TestSampleModel)
"""


class A(models.Model):
    content_type_B = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    object_id_B = models.PositiveIntegerField()
    content_object = EnhancedGenericForeignKey('content_type_B', 'object_id_B')


class B(models.Model):
    content_type_D = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)


class C(models.Model):
    A = models.ForeignKey(A)
    object_id_D = models.PositiveIntegerField(blank=True, null=True)
    content_object_D = EnhancedGenericForeignKey('A.content_object.content_type_D', 'object_id_D')


"""
Field can be property on model.
"""


class Alpha(models.Model):
    text = models.TextField()

    @property
    def content_type(self):
        return ContentType.objects.get_for_model(TestSampleModel)


class Beta(models.Model):
    alpha = models.ForeignKey(Alpha)
    object_id = models.PositiveIntegerField()
    content_object = EnhancedGenericForeignKey('alpha.content_type', 'object_id')
