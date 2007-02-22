from django.conf.urls.defaults import *
from articles.models import *

urlpatterns = patterns('',
    (r'^admin/', include('django.contrib.admin.urls')),
    (r'^$', 'django.views.generic.list_detail.object_list',
     {'queryset': Category.objects.all(),
      'allow_empty': True}),
    (r'^(?P<object_id>[0-9]+)/$', 'django.views.generic.list_detail.object_detail',
     {'queryset': Category.objects.all()}),
    (r'^new/$', 'django.views.generic.create_update.create_object',
     {'model': Category}),
)
