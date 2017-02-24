from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()


urlpatterns = [
    url(r'^', include('usc_app.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^notifications/', include('notify.urls', 'notifications')),
    url(r'^messages/', include('postman.urls','postman')),
]
