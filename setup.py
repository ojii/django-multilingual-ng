from setuptools import setup, find_packages

setup(
    name = 'django-multilingual',
    version = '0.1.0',
    description = 'Multilingual extension for Django',
    author = 'Marcin Kaszynski',
    url = 'http://code.google.com/p/django-multilingual/',
    packages = find_packages(exclude=["testproject", "testproject.*"]),
    zip_safe=False,
    package_data = {
        '': ['templates/*/*.html'],
    },
)
