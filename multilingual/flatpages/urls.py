from django.conf.urls.defaults import *

urlpatterns = patterns('multilingual.flatpages.views',
    (r'^(?P<url>.*)$', 'multilingual_flatpage'),
)
