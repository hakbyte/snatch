from setuptools import setup, find_packages

setup(
    name="snatch",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'requests',
        'termcolor'
    ],
    entry_points={
        'console_scripts': [
            'snatch=src:main',
        ],
    },
)
