#!/usr/bin/env python3
from io import open

from setuptools import find_packages, setup


def read(f):
    return open(f, 'r', encoding='utf-8').read()


setup(
    name='django-multiform-authentication',
    version='0.2',
    url='http://multauth.sigent.com',
    license='BSD',
    description='Combined web and mobile authentication for Django.',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    author='Andrei Vasin',
    packages=find_packages(exclude=['tests', 'example']),
    include_package_data=True,
    install_requires=["django>=2.2"],
    python_requires=">=3.5",
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
