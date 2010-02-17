"""
Multilingual model support.

This code is put in multilingual.models to make Django execute it
during application initialization.

TO DO: remove it.  Right now multilingual must be imported directly
into any file that defines translatable models, so it will be
installed anyway.

This module is here only to make it easier to upgrade from versions
that did not require TranslatableModel.Translation classes to subclass
multilingual.Translation to versions that do.
"""

from translation import install_translation_library
install_translation_library()