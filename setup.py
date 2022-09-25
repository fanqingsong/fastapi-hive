#!/usr/bin/env python

from setuptools import setup, find_packages

with open('requirements.txt', mode="r", encoding="utf8") as f:
    required = f.read().splitlines()

setup(
      name='fastapi_modules',
      version='1.0',
      description='framework for FastAPI Modules',
      url="https://github.com/fanqingsong/fastapi-ml-skeleton",
      license='MIT License',
      author='Qingsong Fan',
      author_email='qsfan@qq.com',
      packages=[
            "fastapi_modules",
            "fastapi_modules.ioc_container",
            "fastapi_modules.ioc_container.module_container",
            "fastapi_modules.ioc_container.module_mounter",
            "fastapi_modules.ioc_container.router_mounter",
      ],
      install_requires=required,
      python_requires=">=3.7",
)
