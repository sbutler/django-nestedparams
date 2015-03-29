#!/usr/bin/env python

from distutils.core import setup

import django_nestedparams

setup(
    name='Django-NestedParams',
    version=django_nestedparams.__version__,
    description='Rails like nested parameters for Django.',
    author='Stephen J. Butler',
    author_email='stephen.butler@gmail.com',
    url='http://publish.illinois.edu/sbutler1/',
    packages=['django_nestedparams'],
)
