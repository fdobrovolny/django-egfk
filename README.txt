Django - **E**nhanced **G**eneric **F**oreign **K**ey
=====================================================

Homepage
--------
Visit the home of `Django-egfk` on the web:
[github.com/BrnoPCmaniak/django-egfk](https://github.com/BrnoPCmaniak/django-egfk)

Documentation
-------------

Example Usage:
models.py:
    from django.db import models
    from django_egfk.fields import GenericForeignKey
    from django.contrib.contenttypes.models import ContentType

    class Main(models.Model):
        text = models.TextField()
        content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)


    class Child(models.Model):
        object_id = models.PositiveIntegerField()
        main = models.ForeignKey(Main, related_name="child")
        content_object = GenericForeignKey('main.content_type', 'object_id')


And now you can do this:
    >>> from test_g.models import Main, Child
    >>> from django.contrib.auth.models import User
    >>> m = Main(text="TEST")
    >>> u = User.objects.get()
    >>> u
    <User: alex>
    >>> m.save()
    >>> m.text
    'TEST'
    >>> c = Child(main=m, content_object=u)
    >>> c.save()
    >>> Main.objects.get().text
    'TEST'
    >>> Main.objects.get().content_type
    <ContentType: user>
    >>> c.content_object
    <User: alex>
