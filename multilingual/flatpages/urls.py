from django.conf.urls.defaults import *
from multilingual.flatpages.views import *

urlpatterns = patterns('',
    url(r'^(?P<url>.*)$', MultilingualFlatPage , name="multilingual_flatpage"),
)
