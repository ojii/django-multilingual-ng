from django.db import models

from multilingual.query import MultilingualModelQuerySet
from multilingual.languages import *


class MultilingualManager(models.Manager):
    """
    A manager for multilingual models.

    TO DO: turn this into a proxy manager that would allow developers
    to use any manager they need.  It should be sufficient to extend
    and additionaly filter or order querysets returned by that manager.
    """

    def get_query_set(self):
        return MultilingualModelQuerySet(self.model)
Manager = MultilingualManager # backwards compat, will be depricated