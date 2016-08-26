from __future__ import unicode_literals

from collections import defaultdict

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import FieldDoesNotExist, ObjectDoesNotExist
from django.db import models
from django.core import checks

from .exceptions import PropertyIsImutable
from .tools import getattrd, getattrd_last_but_one, get_field, get_field_model, setattrd


class EnhancedGenericForeignKey(GenericForeignKey):
    """Enhanced GenericForeignKey.

    For more info take a look at
    django.contrib.contenttypes.fields.GenericForeignKey.

    Inspired by:
    https://github.com/django/django/blob/stable/1.10.x/django/contrib/contenttypes/fields.py#L21  # noqa

    :param autosave_related: Should be related objects saved when this relation
    is set.
    :param type: Boolean

    Enhancements:
    * content_type or contet_id field can be on different model by dot notaion.
    """
    autosave_related = True

    def __init__(self, ct_field='content_type', fk_field='object_id',
                 for_concrete_model=True, autosave_related=True):
        self.autosave_related = autosave_related
        super(EnhancedGenericForeignKey, self).__init__(ct_field, fk_field, for_concrete_model)

    def get_filter_kwargs_for_object(self, obj):
        """See corresponding method on Field"""
        return {
            self.fk_field: getattrd(obj, self.fk_field),
            self.ct_field: getattrd(obj, self.ct_field),
        }

    def _check_object_id_field(self):
        try:
            get_field(self.model, self.fk_field, ignore_GFK=True)
        except FieldDoesNotExist:
            return [
                checks.Error(
                    "The GenericForeignKey object ID references the "
                    "non-existent field '%s'." % self.fk_field,
                    obj=self,
                    id='contenttypes.E001',
                )
            ]
        else:
            return []

    def _check_content_type_field(self):
        """
        Check if field named `field_name` in model `model` exists and is a
        valid content_type field (is a ForeignKey to ContentType).
        """
        try:
            field = get_field(self.model, self.ct_field, ignore_GFK=True)
        except FieldDoesNotExist:
            model = get_field_model(self.model, ".".join(self.ct_field.split(".")[:-1]),
                                    ignore_GFK=True)
            if model is None:
                return []
            elif isinstance(getattr(model,  self.ct_field.split(".")[-1]), property):
                return []
            return [
                checks.Error(
                    "The GenericForeignKey content type references the "
                    "non-existent field '%s.%s'." % (
                        self.model._meta.object_name, self.ct_field
                    ),
                    obj=self,
                    id='contenttypes.E002',
                )
            ]
        else:
            if field is None:
                return []
            elif not isinstance(field, models.ForeignKey):
                return [
                    checks.Error(
                        "'%s.%s' is not a ForeignKey." % (
                            self.model._meta.object_name, self.ct_field
                        ),
                        hint=(
                            "GenericForeignKeys must use a ForeignKey to "
                            "'contenttypes.ContentType' as the 'content_type'"
                            " field."
                        ),
                        obj=self,
                        id='contenttypes.E003',
                    )
                ]
            elif field.remote_field.model != ContentType:
                return [
                    checks.Error(
                        "'%s.%s' is not a ForeignKey to "
                        "'contenttypes.ContentType'." % (
                            self.model._meta.object_name, self.ct_field
                        ),
                        hint=(
                            "GenericForeignKeys must use a ForeignKey to "
                            "'contenttypes.ContentType' as the 'content_type'"
                            " field."
                        ),
                        obj=self,
                        id='contenttypes.E004',
                    )
                ]
            else:
                return []

    def get_prefetch_queryset(self, instances, queryset=None):
        if queryset is not None:
            raise ValueError("Custom queryset can't be used for this lookup.")

        # For efficiency, group the instances by content type and then do one
        # query per model
        fk_dict = defaultdict(set)
        # We need one instance for each group in order to get the right db:
        instance_dict = {}
        for instance in instances:
            # We avoid looking for values if either ct_id or fkey value is None
            ct_model = getattrd_last_but_one(instance, self.ct_field, instance).__class__
            ct_attname = get_field(ct_model, self.ct_field.split(".")[-1]).get_attname()
            full_ct_attname = ("%s.%s" % (".".join(self.ct_field.split(".")[:-1]), ct_attname)
                               if len(self.ct_field.split(".")[:-1]) > 1 else ct_attname)
            ct_id = getattrd(instance, full_ct_attname)
            if ct_id is not None:
                fk_val = getattrd(instance, self.fk_field)
                if fk_val is not None:
                    fk_dict[ct_id].add(fk_val)
                    instance_dict[ct_id] = instance

        ret_val = []
        for ct_id, fkeys in fk_dict.items():
            instance = instance_dict[ct_id]
            ct = self.get_content_type(id=ct_id, using=instance._state.db)
            ret_val.extend(ct.get_all_objects_for_this_type(pk__in=fkeys))

        # For doing the join in Python, we have to match both the FK val and
        # the content type, so we use a callable that returns
        # a (fk, class) pair.
        def gfk_key(obj):
            ct_model = getattrd_last_but_one(obj, self.ct_field, instance).__class__
            ct_attname = get_field(ct_model, self.ct_field.split(".")[-1]).get_attname()
            full_ct_attname = ("%s.%s" % (".".join(self.ct_field.split(".")[:-1]), ct_attname)
                               if len(self.ct_field.split(".")[:-1]) > 1 else ct_attname)
            ct_id = getattrd(obj, full_ct_attname)
            if ct_id is None:
                return None
            else:
                model = self.get_content_type(
                    id=ct_id, using=obj._state.db).model_class()
                return (model._meta.pk.get_prep_value(
                            getattrd(obj, self.fk_field)), model)

        return ret_val, lambda obj: (obj._get_pk_val(), obj.__class__), gfk_key, True, self.name

    def __get__(self, instance, cls=None):
        if instance is None:
            return self

        # Don't use getattr(instance, self.ct_field) here because that might
        # reload the same ContentType over and over (#5570). Instead, get the
        # content type ID here, and later when the actual instance is needed,
        # use ContentType.objects.get_for_id(), which has a global cache.
        ct_model = getattrd_last_but_one(instance, self.ct_field, instance)
        ct_model_class = ct_model.__class__
        try:
            ct_attname = get_field(ct_model_class, self.ct_field.split(".")[-1]).get_attname()
            full_ct_attname = ("%s.%s" % (".".join(self.ct_field.split(".")[:-1]), ct_attname)
                               if len(self.ct_field.split(".")[:-1]) > 1 else ct_attname)
            ct_id = getattrd(instance, full_ct_attname)
        except FieldDoesNotExist as ferror:
            try:
                ct_id = getattr(ct_model,  self.ct_field.split(".")[-1]).id
            except AttributeError:
                raise ferror
        pk_val = getattrd(instance, self.fk_field)

        try:
            rel_obj = getattrd(instance, self.cache_attr)
        except AttributeError:
            rel_obj = None
        else:
            if rel_obj and (
                    ct_id != self.get_content_type(obj=rel_obj, using=instance._state.db).id or
                    rel_obj._meta.pk.to_python(pk_val) != rel_obj._get_pk_val()):
                rel_obj = None

        if rel_obj is not None:
            return rel_obj

        if ct_id is not None:
            ct = self.get_content_type(id=ct_id, using=instance._state.db)
            try:
                rel_obj = ct.get_object_for_this_type(pk=pk_val)
            except ObjectDoesNotExist:
                pass
        setattr(instance, self.cache_attr, rel_obj)
        return rel_obj

    def __set__(self, instance, value):
        ct = None
        fk = None
        if value is not None:
            ct = self.get_content_type(obj=value)
            fk = value._get_pk_val()

        try:
            setattrd(instance, self.ct_field, ct)
        except AttributeError as e:
            if e.message != "can't set attribute":
                raise
            elif getattrd(instance, self.ct_field).id != ct.id:
                raise PropertyIsImutable()
        if "." in self.ct_field and self.autosave_related:
            getattrd_last_but_one(instance, self.ct_field).save()
        setattrd(instance, self.fk_field, fk)
        if "." in self.fk_field and self.autosave_related:
            getattrd_last_but_one(instance, self.fk_field).save()
        setattrd(instance, self.cache_attr, value)

    def get_related_model(self, instance):
        ct_attname = get_field(self.model, self.ct_field).get_attname()
        ct_id = getattrd(instance, ct_attname)
        return self.get_content_type(id=ct_id).model_class()
