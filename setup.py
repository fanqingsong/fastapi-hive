#!/usr/bin/env python

from setuptools import setup, find_packages

with open('requirements.txt', mode="r", encoding="utf8") as f:
    required = f.read().splitlines()

setup(
      name='FastAPI Skeleton',
      version='1.1',
      description='Sample code for FastAPI',
      url="https://github.com/fanqingsong/fastapi-ml-skeleton",
      license='MIT License',
      author='Qingsong Fan',
      author_email='qsfan@qq.com',
      packages=find_packages(),
      install_requires=required,
      python_requires=">=3.7",
)
