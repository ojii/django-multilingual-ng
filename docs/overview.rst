===================
Django Multilingual
===================


Configuration
=============

After following the instructions over at ``INSTALL``, we need to configure our
app's ``settings.py`` file.

* Add ``LANGUAGES`` setting this is the same setting that is used by Django's
  i18n::

    LANGUAGES = (
        ('en', 'English'),
        ('pl', 'Polish'),
    )

* Add ``DEFAULT_LANGUAGE``, in this example setting it to 1 would make the
  default English as it is first in the ``LANGUAGES`` list::

    DEFAULT_LANGUAGE = 1

* Add multilingual.context_processors.multilingual to ``TEMPLATE_CONTEXT_PROCESSORS``,
  it should look something like this::

    TEMPLATE_CONTEXT_PROCESSORS = (
        'django.core.context_processors.auth',
        'django.core.context_processors.debug',
        'django.core.context_processors.i18n',
        'multilingual.context_processors.multilingual',
    )

* Add multilingual to ``INSTALLED_APPS``, it should look like this::

    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.admin',
        'multilingual',
    )

Model Setup
===========

Once this is done, we need to setup our Model.

* At the top of the model file import multilingual::

    import multilingual

* Create the model, the sub-class translation contains all the fields that
  will have multiple language data. For example::

    class Category(models.Model):
        parent = models.ForeignKey('self', blank=True, null=True)

        class Translation(multilingual.Translation):
            name = models.CharField(max_length=250)

        def __unicode__(self):
            return self.name

``Meta`` Class
==============

You may also add a ``Meta`` inner class to the ``Translation`` class to
configure the translation mechanism. Currently, the only properties
recognized is::

    db_table sets the database table name (default: <model>_translation) 

An example::

    class Dog(models.Model):
        owner = models.ForeignKey(Human)

        class Translation(multilingual.Translation):
            breed = models.CharField(max_length=50)

            class Meta:
                db_table = 'dog_languages_table'

.. vi:ft=rst:expandtab:shiftwidth=4
