# -*- coding: utf-8 -*-

from setuptools import setup
from django_egfk import __version__
import os
import io

HERE = os.path.abspath(os.path.dirname(__file__))


def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

setup(
    name='django-egfk',
    version=__version__,
    platforms=['OS Independent'],
    description='Add django enhanced Generic Foreignkey.',
    # long_description=read('README.txt', 'CHANGES.txt'),
    keywords='django generic foreignkey',
    url='https://github.com/monterail/django-egfk',
    author='Filip Dobrovolny',
    author_email='brnopcman@gmail.com',
    license='MIT',
    maintainer='Filip Dobrovolny',
    maintainer_email='brnopcman@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
    packages=['django_egfk'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'django',
    ],
)
