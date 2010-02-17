from setuptools import setup, find_packages

version = __import__('multilingual').__version__

setup(
    name = 'django-multilingual-ng',
    version = '1.0.0b1',
    description = 'Multilingual extension for Django - NG',
    author = 'Jonas Obrist',
    url = 'http://github.com/ojii/django-multilingual-ng',
    packages = find_packages(exclude=["testproject",]),
    zip_safe=False,
    package_data = {
        '': ['templates/*/*.html'],
    },
)
