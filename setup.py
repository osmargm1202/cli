# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    packages=find_packages(),
    package_data={
        "orgm": ["*",],
    },
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "orgm=orgm.orgm:main",
        ],
    },
    description="CLI de ORGM para gestionar proyectos y tareas",
    author="Osmar Garcia",
    author_email="osmargm1202@gmail.com",
    url="https://github.com/osmargm1202/cli.git",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
