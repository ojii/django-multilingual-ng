################################
Changes from django-multilingual
################################

****************
Database Changes
****************

* The ``language_id`` field in the translation model has been deprecated in favor
of a ``lanuage_code`` field. This allows you to change ``settings.LANGUAGES`` without
having to worry too much. It also makes custom queries filtering for languages a
lot more intiutive

**************
Python Changes
**************

Functions and Methods
=====================

* Due to the database changes, all functions and methods using ``language_id`` now
use ``language_code``.
* Functions and methods which returned a ``language_id`` are no longer
available since they don't are no longer useful.

Names
=====

All name changes will be kept for backwards compatiblity at least until version
0.4.0. 

* All names in the main multilingual module (``multilingual.__init__``) are going
to be deprecated. Please import all names in their from
their actual origin. For example instead of ``from multilingual import get_default_language``
use ``from multilingual.languages import get_default_language``.

* ``multilingual.translation.Translation`` (and ``multilingual.Translation``) is
now called ``multilingual.translation.TranslationModel``.

* ``multilingual.manager.Manager`` (and ``multilingual.Manager``) is now called
``multilingual.manager.MultilingualManager``.

* ``multilingual.admin.ModelAdmin`` (and ``multilingual.ModelAdmin``) is now called
``multilingual.admin.MultilingualModelAdmin``.

****************
Template Changes
****************

* The default admin change form template for ``multilingual.admin.MultilingualModelAdmin``
has been changed to use tabbed languages for a nicer interface.

************
New Features
************

* ``mulitlingual.admin.MultilingualInlineAdmin``
* The Global Language Lock.