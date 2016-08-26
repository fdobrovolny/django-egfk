"""Handy tools.

List:
* getattrd() - getattr with dot notation
* getattrd_last_but_one() - getattrd "[-2]" object in notation
* setattrd() - setattr with dot notation
* get_field() - same as model._meta.get_field but adds support for model
traversing
"""
from __future__ import unicode_literals

from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models import ForeignKey


class NoDefaultProvided(object):
    """Exception for *attr functions."""

    pass


def getattrd(obj, name, default=NoDefaultProvided):
    """Better version of getattr().

    Same as getattr(), but allows dot notation lookup.
    Discussed in:
    http://stackoverflow.com/questions/11975781
    """
    try:
        return reduce(getattr, name.split("."), obj)
    except (AttributeError,):
        if default != NoDefaultProvided:
            return default
        raise


def getattrd_last_but_one(obj, name, default=NoDefaultProvided):
    """Same as getattrd(), but leaves out last ".foo" part.

    e.g. name="branch.apple.color" obj = tree -> tree.branch.apple
    """
    try:
        return reduce(getattr, name.split(".")[:-1], obj)
    except (AttributeError,):
        if default != NoDefaultProvided:
            return default
        raise


def setattrd(obj, name, value):
    """Better version of setattr().

    Same as setattr(), but allows dot notation lookup.
    """
    try:
        name = name.split(".")
        return setattr(reduce(getattr, name[:-1], obj), name[-1], value)
    except AttributeError:
        raise


class GenericForeignKeyDetected(AttributeError):
    pass


def get_field(model, field_name, ignore_GFK=False):
    """Get field with . notaion for traversing between objects."""
    def jump(a, b):
        if b[-1] != "*":
            f = a._meta.get_field(b)
            if isinstance(f, ForeignKey):
                return f.related_model
            elif isinstance(f, GenericForeignKey):
                raise GenericForeignKeyDetected()
            return f
        else:
            return a._meta.get_field(b[:-1])
    try:
        return reduce(jump, (field_name+"*").split("."), model)
    except GenericForeignKeyDetected:
        if ignore_GFK:
            return None
        raise
