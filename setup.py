import sys
from setuptools import setup

setup(
    name = 's3scrot',
    version = '1.0',
    description = 'Tool to capture and upload screenshots to Amazon S3',
    author = 'Ryan McGuire',
    author_email = 'ryan@enigmacurry.com',
    url = 'https://github.com/EnigmaCurry/s3scrot',
    install_requires = ['boto'],
    packages=["s3scrot"],
    zip_safe=False,
    entry_points = {
        'console_scripts': ['s3scrot = s3scrot.s3scrot:main']},
)
