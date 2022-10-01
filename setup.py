#!/usr/bin/env python

from distutils.core import setup
# from setuptools import setup

# with open('requirements.txt', mode="r", encoding="utf8") as f:
#     required = f.read().splitlines()

setup(
      name='fastapi_hive',
      version='1.0',
      description='framework for FastAPI modules management',
      url="https://github.com/fanqingsong/fastapi-ml-skeleton",
      license='MIT License',
      author='Qingsong Fan',
      author_email='qsfan@qq.com',
      packages=[
            "fastapi_hive",
            "fastapi_hive.ioc_framework",
            "fastapi_hive.ioc_framework.module_container",
            "fastapi_hive.ioc_framework.module_abstraction",
            "fastapi_hive.ioc_framework.module_mounter",
            "fastapi_hive.ioc_framework.router_mounter",
      ],
      # install_requires=required,
      # python_requires=">=3.7",
)
