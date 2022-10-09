#!/usr/bin/env python

from setuptools import setup

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='fastapi_hive',
    version='1.0.8',
    description='framework for FastAPI modules management',
    long_description_content_type='text/markdown',
    long_description=long_description,
    url="https://github.com/fanqingsong/fastapi-hive",
    keywords="fastapi machine-learning packages modules",
    license='Apache-2.0 license',
    author='Qingsong Fan',
    author_email='qsfan@qq.com',
    project_urls={
        "Issue Tracker": "https://github.com/fanqingsong/fastapi-hive/issues",
        "Documentation": "https://fanqingsong.github.io/fastapi-hive/",
    },
    package_dir = {'fastapi_hive': 'fastapi_hive'},
    python_requires=">=3.7",
    install_requires=[
        'fastapi>=0.48.0',
        'loguru>=0.4.1',
        'dependency-injector>=4.40.0',
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
