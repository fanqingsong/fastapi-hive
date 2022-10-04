#!/usr/bin/env python

# from distutils.core import setup
from setuptools import setup
import os

# with open('requirements.txt', mode="r", encoding="utf8") as f:
#     required = f.read().splitlines()

# read the contents of your README file
# from pathlib import Path
# this_directory = Path(__file__).parent
# long_description = (this_directory / "README.md").read_text()

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()


def read_requirements():
    """Parse requirements from requirements.txt."""
    reqs_path = os.path.join('.', 'requirements.txt')
    with open(reqs_path, 'r') as f:
        requirements = [line.rstrip() for line in f]
    return requirements


setup(
      name='fastapi_hive',
      version='1.0.1',
      description='framework for FastAPI modules management',
      long_description_content_type='text/markdown',
      long_description=long_description,
      url="https://github.com/fanqingsong/fastapi-hive",
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
      # install_requires=read_requirements(),
      python_requires=">=3.7",
      # other arguments omitted
)
