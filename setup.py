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


# install_requires = open("requirements.txt", "rb").read().decode("utf-8")


setup(
    name='fastapi_hive',
    version='1.0.5',
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
    # packages=[
    #     "fastapi_hive",
    #     "fastapi_hive.ioc_framework",
    #     "fastapi_hive.ioc_framework.module_container",
    #     "fastapi_hive.ioc_framework.module_abstraction",
    #     "fastapi_hive.ioc_framework.module_mounter",
    #     "fastapi_hive.ioc_framework.router_mounter",
    # ],
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
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
)
