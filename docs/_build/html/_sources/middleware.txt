==========================================
Add middleware to set the default language
==========================================

Django contains middleware that automatically discovers the browser's language
and allows the user to change it. All translated strings in Python code and
templates are then automatically shown in this language. (See the official
Django documentation.) You can use the same language as the default translation
for model fields.

Add ``multilingual.middleware.DefaultLanguageMiddleware`` to your ``MIDDLEWARE_CLASSES``::

    MIDDLEWARE_CLASSES = (
        #...
        'django.middleware.locale.LocaleMiddleware',
        'multilingual.middleware.DefaultLanguageMiddleware',
        #...
    )

The multilingual middleware must come after the language discovery middleware,
in this case ``django.middleware.locale.LocaleMiddleware``. 

.. vi:ft=rst:expandtab:shiftwidth=4
