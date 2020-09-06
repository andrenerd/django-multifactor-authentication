#!/usr/bin/env python3
from io import open

from setuptools import find_packages, setup


def read(f):
    return open(f, 'r', encoding='utf-8').read()


setup(
    name='django-multifactor-authentication',
    version='0.9.3',
    url='https://github.com/andrenerd/django-multifactor-authentication',
    license='BSD',
    description='Flexible authentication for web, mobile, desktop and hybrid apps. It can be used for 1fa, 2fa and mfa cases.',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    author='Andrei Vasin',
    packages=find_packages(exclude=['tests', 'example']),
    include_package_data=True,
    install_requires=[
        'django>=2.2, <4.0.0',
        'djangorestframework>=3.10.3, <4.0.0',
        'phonenumbers>=8.0.0', # required by django-phonenumber-field only
        'django-phonenumber-field>=3.0.1',
        'django_otp>=0.4.3',
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
        'Source': 'https://github.com/andrenerd/django-multifactor-authentication',
    },
)
