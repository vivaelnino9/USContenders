from django.conf.urls import include, url
from django.conf.urls.static import static
from django.conf import settings


from usc_app import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^rosters', views.roster_table, name='rosters'),
    url(r'^team/(?P<team_name>[\w|\W]+)/$',views.team_page, name='team'),
    url(r'^player/(?P<team_name>[\w|\W]+)/(?P<player_name>[\w|\W]+)/$',views.player_page, name='player'),
    url(r'^challenge/$', views.challenge, name='challenge'),
    url(r'^challenge/(?P<team_challenged>[\w|\W]+)/$', views.challenge_with_arg, name='challenge_arg'),
    url(r'^results/$', views.results, name='results'),
    url(r'^results/(?P<match_id>[\w|\W]+)/$$', views.game_results, name='game_results'),
    url(r'^register/$', views.captain_register, name='register'),
    url(r'^login/$', views.captain_login, name='login'),
    url(r'^logout/$', views.captain_logout, name='logout'),
    url(r'^success/$', views.challenge_success, name='success'),
]
