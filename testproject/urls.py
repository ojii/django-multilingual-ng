from django.conf.urls.defaults import *
from django.contrib import admin
from articles.models import *

admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'django.views.generic.list_detail.object_list',
     {'queryset': Category.objects.all(),
      'allow_empty': True}),
    (r'^(?P<object_id>[0-9]+)/$', 'django.views.generic.create_update.update_object',
     {'model': Category,
      'post_save_redirect': '/'}),
    (r'^new/$', 'django.views.generic.create_update.create_object',
     {'model': Category}),

    (r'^admin/(.*)', admin.site.root),
)
