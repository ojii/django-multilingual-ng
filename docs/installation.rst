############
Installation
############


**************
Install Django
**************

django-multilingual-ng requires you to have Django 1.2 (or higher) installed. 
You can get it from www.djangoproject.com and follow the instructions at
http://docs.djangoproject.com/en/dev/intro/install/.

**********************************************************
Install South (only if upgrading from django-multilingual)
**********************************************************

To upgrade from django-multilingual and use the ``mlng_convert`` command you must
have south installed. You may get it from `south.aeracode.org <http://south.aeracode.org/>`_.
Note that the current stable release at the time of writing (0.6.2) is not
compatible with Django 1.2.

******************************
Install django-multilingual-ng
******************************

Stable Version
==============

There is currently no stable version

Unstable Version
================

Installing from git
-------------------

Clone the git repository at ``git://git@github.com:ojii/django-multilingual-ng.git`` and
run ``python setup.py install``

Installing from tarball
-----------------------

Download the latest development snapshot from
http://github.com/ojii/django-multilingual-ng/tarball/master, untar it and run
``python setup.py install``

**********************************
Migrating from django-multilingual
**********************************

If you are migrating from django-multilingual, you have to convert your database
to the new format. Additionally note that all names currently in the main
multilingual namespace are going to be deprecated. Please import them from their
respective subnamespace, for example
``from multilingual.translation import TranslationModel`` instead of 
``from multilingual import Translation``. A full list of things to be deprecated
can be viewed on http://wiki.github.com/ojii/django-multilingual-ng/deprecation.

Migrating the database
======================

**Please make a backup of your database before you start migrating your database**

django-multilingual-ng does not use ``language_id`` anymore, instead it uses
``language_code`` to be independent from the settings file. Thus all current
models using translations you have in your projects need those fields migrated.

django-multilingual-ng provides a handy command called ``mlng_convert`` which
can be called with an app name as argument to convert all multilingual models in
that app to the new format. Note that this command will delete the language_id
column and all it's data from the database, so make sure you have a backup of
your database.

If you wish to migrate by hand, feel free to do so. Ideally you write a custom
south migration to do the changes. Read the source of the ``mlng_convert``
command for pointers. 

**Please note that** ``schemamigration <appname> <migrationname> --auto`` **with south
will most likely not work properly.**

If you do want to use south to migrate from django-multilingual to django-multilingual-ng,
please write the migration by hand.