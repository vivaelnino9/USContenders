from django.conf.urls import include, url
from django.conf.urls.static import static
from django.conf import settings


from usc_app import views
from postman.views import WriteView, MessageView, ConversationView, InboxView

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^rosters', views.roster_table, name='rosters'),
    url(r'^search', views.search, name='search'),
    url(r'^team/(?P<team_name>[\w|\W]+)/$',views.team_page, name='team'),
    url(r'^player/(?P<team_name>[\w|\W]+)/(?P<player_name>[\w|\W]+)/$',views.player_page, name='player'),
    url(r'^add/(?P<team_name>[\w|\W]+)/(?P<field>[\w|\W]+)/(?P<player_name>[\w|\W]+)/$', views.add_player, name='add_player'),
    url(r'^drop/(?P<team_name>[\w|\W]+)/(?P<player_name>[\w|\W]+)/$', views.drop_player, name='drop_player'),
    url(r'^check_username/$', views.check_username, name='check_username'),
    url(r'^challenge/$', views.challenge, name='challenge'),
    url(r'^challenge/(?P<team_challenged>[\w|\W]+)/$', views.challenge_with_arg, name='challenge_arg'),
    url(r'^results/$', views.results, name='results'),
    url(r'^team_register/$', views.team_register, name='team_register'),
    url(r'^player_register/$', views.player_register, name='player_register'),
    url(r'^login/$', views.captain_login, name='login'),
    url(r'^logout/$', views.captain_logout, name='logout'),
    url(r'^notifications/$', views.notifications, name='notifications'),
    url(r'^submit/(?P<challenge_id>[\w|\W]+)/$', views.score_submit, name='submit'),
    url(r'^accept_score/(?P<challenge_id>[\w|\W]+)//(?P<g1_id>[\w|\W]+)//(?P<g2_id>[\w|\W]+)/$', views.accept_score, name='accept_score'),
    url(r'^reject_score/(?P<challenge_id>[\w|\W]+)/$', views.reject_score, name='reject_score'),
    url(r'^forfeit/(?P<challenge_id>[\w|\W]+)/$',views.forfeit, name='forfeit'),
    url(r'^success/$', views.challenge_success, name='success'),
    url(r'^messages/write/(?:(?P<recipients>[^/#]+)/)?$', WriteView.as_view(template_name='write.html'), name='write'),
    url(r'^messages/inbox/(?:(?P<option>m)/)?$', InboxView.as_view(template_name='inbox.html'), name='inbox'),
    url(r'^messages/view/(?P<message_id>[\d]+)/$', MessageView.as_view(template_name='view.html'), name='message_view'),
    url(r'^messages/view/t/(?P<thread_id>[\d]+)/$', ConversationView.as_view(template_name='view.html'), name='conversation_view'),
]
