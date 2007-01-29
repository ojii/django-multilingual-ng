"""
Multilingual model support.

This code is put in multilingual.models to make Django execute it
during application initialization.
"""

from translation import install_translation_library
install_translation_library()
