from django.conf.urls.defaults import *
from articles.models import *

urlpatterns = patterns('',
    (r'^$', 'django.views.generic.list_detail.object_list',
     {'queryset': Category.objects.all(),
      'allow_empty': True}),
    (r'^(?P<object_id>[0-9]+)/$', 'django.views.generic.create_update.update_object',
     {'model': Category,
      'post_save_redirect': '/'}),
    (r'^new/$', 'django.views.generic.create_update.create_object',
     {'model': Category}),
)

# handle both newforms and oldforms admin URL

from multilingual.compat import IS_NEWFORMS_ADMIN
if IS_NEWFORMS_ADMIN:
    from django.contrib import admin

    urlpatterns += patterns('',
        (r'^admin/(.*)', admin.site.root),
    )
else:
    urlpatterns += patterns('',
        (r'^admin/', include('django.contrib.admin.urls')),
    )
