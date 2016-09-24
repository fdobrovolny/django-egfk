Django - **E**nhanced **G**eneric **F**oreign **K**ey
=====================================================

Homepage
--------

Visit the home of `Django-egfk` on the web:
[github.com/BrnoPCmaniak/django-egfk](https://github.com/BrnoPCmaniak/django-egfk)

Documentation
-------------

Features: \* content\_type and object\_id can be on different model
which is connected via ForeignKey, OneToOneField or
EnhancedGenericForeignKey \* content\_type can be a property. The
property have to be ContentType instance.

Example Usage: models.py

``` {.python}
from django.db import models
from django_egfk.fields import EnhancedGenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Main(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)


class Child(models.Model):
    object_id = models.PositiveIntegerField()
    main = models.ForeignKey(Main, related_name="child")
    content_object = EnhancedGenericForeignKey('main.content_type', 'object_id')
```

And now you can do this:

``` {.python}
>>> from test_egfk.models import Main, Child, TestSampleModel
>>> m = Main()
>>> print(m.content_type)
None
>>> m.save()
>>> t = TestSampleModel(text="Test")
>>> t.save()
>>> t.text
'Test'
>>> c = Child(main=m, content_object=t)
>>> c.save()
>>> Main.objects.last().content_type
<ContentType: test sample model>
>>> c.content_object
<TestSampleModel: TestSampleModel object>
```

You can even have neasted EnhancedGenericForeignKey. More info in
example/test\_egfk/models.py @A,B,C,D
