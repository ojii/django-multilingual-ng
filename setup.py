from setuptools import setup, find_packages

version = __import__('multilingual').__version__

setup(
    name = 'django-multilingual-ng',
    version = version,
    description = 'Multilingual extension for Django - NG',
    author = 'Jonas Obrist',
    url = 'http://github.com/ojii/django-multilingual-ng',
    packages = find_packages(exclude=['parts','downloads','eggs', '.installed.cfg', 'bin', 'develop-eggs']),
    zip_safe=False,
    package_data={
        'multilingual': [
            'templates/admin/*.html',
            'templates/admin/multilingual/*.html',
            'templates/admin/multilingual/edit_inline/*.html',
            'flatpages/templates/flatpages/*.html',
            'media/multilingual/admin/css/style.css',
        ],
    },
)