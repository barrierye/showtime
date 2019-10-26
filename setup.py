#-*- coding:utf8 -*-
# Copyright (c) 2019 barriery
# Python release: 3.7.0
import re
from setuptools import setup, find_packages

setup(
    name = 'show-time',
    version = '0.0.2',
    description = 'A spider that crawls the time of various shows.',
    url = 'https://github.com/barrierye/showtime',
    keywords = 'show play spider',
    
    author = 'barriery',
    author_email = 'barriery@qq.com',
    maintainer = 'barriery',
    maintainer_email = 'barriery@qq.com',

    include_package_data=True,

    python_requires='>=3.5',

    install_requires=[
        'beautifulsoup4==4.8.1',
        'lxml==4.4.1',
        'aiohttp==3.6.2',
        'requests==2.22.0',
        'protobuf==3.10.0',
    ],

    packages = find_packages(where='.'),
)
