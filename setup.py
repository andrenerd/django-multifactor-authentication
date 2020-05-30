#!/usr/bin/env python3
from io import open

from setuptools import find_packages, setup


def read(f):
    return open(f, 'r', encoding='utf-8').read()


setup(
    name='django-multiform-authentication',
    version='0.3.0',
    url='http://multauth.sigent.com',
    license='BSD',
    description='Combined web and mobile authentication for Django.',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    author='Andrei Vasin',
    packages=find_packages(exclude=['tests', 'example']),
    include_package_data=True,
    install_requires=[
        'django>=2.2',
        'hashids>=1.2.0',
        'phonenumbers>=8.0.0', # required by django-phonenumber-field only
        'django-formtools>=2.1', # two-factor needs it "explicitly"
        'django-phonenumber-field>=3.0.1',
        'django_otp>=0.4.3',
        'twilio>=6.10.2', # remove, make it optional
        'djangorestframework>=3.10.3, <4.0.0',
        'django-cors-headers==2.1.0', # temp ???
        'django-extra-fields>=0.9', # what ???
        'drf-yasg>=1.16.1', # what ???
        'packaging', # till drf-yasg fixed
        'django-localflavor>=1.6.2', # what ???
        'django-model-utils==3.0.0', # what ???
    ],
    python_requires='>=3.5',
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    project_urls={
        'Source': 'https://github.com/andrenerd/django-multiform-authentication',
    },
)
