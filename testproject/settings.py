# Django settings for testproject project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'           # 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = 'database.db3'             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. All choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en'

# django-multilanguange #####################

# It is important that the language identifiers are consecutive
# numbers starting with 1.

LANGUAGES = [['en', 'English'], # id=1
             ['pl', 'Polish'],  # id=2
             ['zh-cn', 'Simplified Chinese'], # id=3
             ]

DEFAULT_LANGUAGE = 1

##############################################

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '1+t11&r9nw+d7uw558+8=#j8!8^$nt97ecgv()-@x!tcef7f6)'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'multilingual.flatpages.middleware.FlatpageFallbackMiddleware',
)

ROOT_URLCONF = 'testproject.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '../multilingual/templates/',
    'templates/',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'multilingual',
    'multilingual.flatpages',
    'testproject.articles',
    'testproject.fallback',
    'testproject.inline_registrations',
    'testproject.issue_15',
    'testproject.issue_16',
    'testproject.issue_23',
    'testproject.issue_29',
    'testproject.issue_37',
    'testproject.issue_61',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'multilingual.context_processors.multilingual',
)

MULTILINGUAL_FALLBACK_LANGUAGES = ['zh-cn', 'pl']

try:
    # install the debug toolbar if available
    import debug_toolbar

    MIDDLEWARE_CLASSES = (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
        ) + MIDDLEWARE_CLASSES
    INSTALLED_APPS += ('debug_toolbar',)

    INTERNAL_IPS = ('127.0.0.1',)

    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False
        }

except ImportError:
    pass
