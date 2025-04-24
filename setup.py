# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

setup(
    packages=find_packages(),
    package_data={
        'orgm': ['*.md', '*.json', '*.txt', 'data/*', 'stuff/*', 'adm/*', 'questionary/*'],
    },
    include_package_data=True,
) 