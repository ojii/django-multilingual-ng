"""
Django-multilingual: a QuerySet subclass for models with translatable
fields.

Also, a wrapper for lookup_inner that makes it possible to lookup via
translatable fields.
"""

from compat import IS_QSRF

if IS_QSRF:
    from compat.query_post_qsrf import MultilingualModelQuerySet
else:
    from compat.query_pre_qsrf import MultilingualModelQuerySet
