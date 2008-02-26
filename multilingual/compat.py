"""
Code that allows DM to be compatible with various Django versions.
"""

# check whether Django is from the newforms-admin branch
IS_NEWFORMS_ADMIN = False

try:
    # try to import a class that is no longer present in the
    # newforms-admin branch
    from django.contrib.admin.templatetags.admin_modify import StackedBoundRelatedObject
except ImportError:
    IS_NEWFORMS_ADMIN = True
