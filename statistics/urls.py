from django.conf.urls import include, url
from django.contrib import admin

import views


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^get_scores/?$', views.get_scores, name='get_scores'),
    url(r'^get_scores/(?P<topic>\w+)/?$', views.get_scores, name='get_scores'),
]
