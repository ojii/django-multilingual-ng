======================
Multilingual Flatpages
======================


The Django flatpages application is "[...] a simple object with a URL, title and
content. Use it for one-off, special-case pages, such as 'About' or 'Privacy Policy'
pages, that you want to store in a database but for which you don’t want to develop
a custom Django application."

If you have a website in multiple languages you will want to have these pages in
your supported languages. Django-multilingual comes with a version of flatpages
that has translatable name and content fields. You install it by adding
``multilingual.flatpages`` to the installed applications list::

    INSTALLED_APPS = (
        ...
        'multilingual',
        'multilingual.flatpages',
        ...
    )

The multilingual flatpages should now be available in the admin interface. They
use the same templates as the original flatpages application: ``flatpages/base.html``.

You will want to enable the middleware Django Multilingual provides if you want your
pages to appear in the correct language automatically::

    MIDDLEWARE_CLASSES = (
        ...
        'multilingual.flatpages.middleware.FlatpageFallbackMiddleware',
    )

.. vi:ft=rst:expandtab:shiftwidth=4
