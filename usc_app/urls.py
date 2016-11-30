from django.conf.urls import include, url
from django.conf.urls.static import static
from django.conf import settings


from usc_app import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^rosters', views.roster_table, name='rosters'),
    url(r'^team/(?P<team_name>[\w|\W]+)/$',views.team_page, name='team'),
    url(r'^player/(?P<player_name>[\w|\W]+)/$',views.player_page, name='player'),
    url(r'^test',views.test, name='test'),
    url(r'^challenge/$', views.challenge, name='challenge'),
    # url(r'^register/$', views.register, name='register'),
    # url(r'^login/$', views.user_login, name='login'),
    # url(r'^logout/$', views.user_logout, name='logout'),
    # url(r'^profile/(?P<inv_user_id>[0-9]+)/$', views.profile, name='profile'),

]
