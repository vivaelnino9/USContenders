import django_tables2 as tables
from usc_app.models import *
from django.core.urlresolvers import reverse
from django_tables2.utils import A
from django.utils.html import format_html

class RosterTable(tables.Table):
    team_name = tables.LinkColumn(
        'team',
        args=[A('team_name')],
        verbose_name="Team",
        )
    rank = tables.Column(verbose_name="Rank")
    captain = tables.LinkColumn('player',args=[A('team_name'),A('captain')],orderable=False, verbose_name="Captain")
    co_captain = tables.LinkColumn(
        'player',args=[A('team_name'),A('co_captain')],
        orderable=False,
        verbose_name="Co-Captain"
        # default="",
    )
    member1 = tables.LinkColumn(
        'player',args=[A('team_name'),A('member1')],
        orderable=False,
        verbose_name="Member",
        # default="",
    )
    member2 = tables.LinkColumn(
        'player',args=[A('team_name'),A('member2')],
        orderable=False,
        verbose_name="Member",
        # default="",
    )
    member3 = tables.LinkColumn(
        'player',args=[A('team_name'),A('member3')],
        orderable=False,
        verbose_name="Member",
        # default="",
    )
    member4 = tables.LinkColumn(
        'player',args=[A('team_name'),A('member4')],
        orderable=False,
        verbose_name="Member",
        # default="",
    )
    member5 = tables.LinkColumn(
        'player',args=[A('team_name'),A('member5')],
        orderable=False,
        verbose_name="Member",
        # default="",
    )
    member6 = tables.LinkColumn(
        'player',args=[A('team_name'),A('member6')],
        orderable=False,
        verbose_name="Member",
        # default="",
    )
    server = tables.Column(verbose_name="Server")
    class Meta:
        model = Roster
        sequence = ('team_name','rank','captain','co_captain','member1','member2','member3','member4','member5','member6','server')
        exclude = ('id','firstActive','daysActive','logo','abv')
        attrs = {'class': 'table'}
        row_attrs = {
            'class': lambda record: 'diamond' if record.rank < 6 else 'gold' if record.rank < 21 and record.rank > 5 else 'silver' if record.rank > 20 else 'none'
        }
class StatsTable(tables.Table):
    change = tables.Column(
        orderable=False,
        verbose_name="▲▼",
        attrs={'td': {'id': 'change'}},
    )
    streak = tables.Column(
        orderable=False,
        verbose_name="Streak",
        attrs={'td': {'id': 'streak'}},
    )
    highestRank = tables.Column(
        orderable=False,
        verbose_name="Highest Rank",
        attrs={'td': {'id': 'highestRank'}}
    )
    uscmRank = tables.Column(orderable=False,verbose_name="USCM Rank")
    challengeOut = tables.Column(
        orderable=False,
        verbose_name="Challenges Out",
        attrs={'td': {'id': 'challengeOut'}}
    )
    challengeIn = tables.Column(
        orderable=False,
        verbose_name="Challenges In",
        attrs={'td': {'id': 'challengeIn'}}
    )
    GP = tables.Column(
        orderable=False,
        attrs={'th':{'title':'Games Played'}}
    )
    W = tables.Column(
        orderable=False,
        attrs={'th':{'title':'Wins'}}
    )
    L = tables.Column(
        orderable=False,
        attrs={'th':{'title':'Losses'}}
    )
    D = tables.Column(
        orderable=False,
        attrs={'th':{'title':'Draws'}}
    )
    F = tables.Column(
        orderable=False,
        attrs={'th':{'title':'Forfeits'}}
    )
    CF = tables.Column(
        orderable=False,
        attrs={'th':{'title':'Caps For'}}
    )
    CA = tables.Column(
        orderable=False,
        attrs={'th':{'title':'Caps Against'}}
    )
    CD = tables.Column(
        orderable=False,
        attrs={'th':{'title':'Caps Differential'}}
    )
    CDperG = tables.Column(
        orderable=False,
        attrs={'th':{'title':'Caps Differential Per Game'}},
        verbose_name="CD/G",
    )
    class Meta:
        model = Stats
        exclude = ('id','lastActive','team','abv','rank')
        attrs = {
            'class': 'subTeamStats table',
            'align': 'center',
        }

    def render_uscmRank(self,value):
        if value == 0:
            value = '-'
        return value
    def render_highestRank(self,value):
        if value == 0:
            value = '-'
        return value
class ResultsTable(tables.Table):
    challenger = tables.LinkColumn('team',args=[A('challenger')])
    challenged = tables.LinkColumn('team',args=[A('challenged')])
    g1_results = tables.URLColumn(orderable=False,)
    g2_results = tables.URLColumn(orderable=False,)
    class Meta:
        model = Challenge
        exclude = ('id',)
        attrs = {'class': 'table current'}
        row_attrs = {
            'id': lambda record: 'P' + str(record.played)
        }

    def render_g1_results(self,value):
        return format_html('<a target="_blank" href="https://tagpro.eu/?match={}" />#{}', value,value)
    def render_g2_results(self,value):
        return format_html('<a target="_blank" href="https://tagpro.eu/?match={}" />#{}', value,value)

class FATable(tables.Table):
    tagpro_profile = tables.URLColumn(attrs={'a':{'target':'_blank'}},orderable=False,)
    reddit_info = tables.URLColumn(attrs={'a':{'target':'_blank'}},orderable=False,)
    tagpro_stats = tables.URLColumn(verbose_name="TagPro Stats",attrs={'a':{'target':'_blank'}},orderable=False,)
    additional_notes = tables.Column(verbose_name="Additional Notes",orderable=False,)
    class Meta:
        model = FreeAgent
        exclude = ('id','user')
        attrs = {'class': 'table current'}

    def render_tagpro_profile(self,value):
        return format_html('<a target="_blank" href="{}" style="color:#2b2b2b;" />Tagpro', value,value)
    def render_reddit_info(self,value):
        return format_html('<a target="_blank" href="{}" style="color:#ff4500;" />Reddit', value,value)
    def render_tagpro_stats(self,value):
        return format_html('<a target="_blank" href="{}" style="color:#428bca;" />Stats', value,value)

class CurrentChallenges(tables.Table):
    challenger = tables.LinkColumn(
        'team',
        args=[A('challenger')],
        verbose_name="Challenger",
        orderable=False,
    )
    challenged = tables.LinkColumn(
        'team',
        args=[A('challenged')],
        verbose_name="Challenged",
        orderable=False,
    )
    map = tables.Column(orderable=False,)
    challenge_date = tables.DateColumn(
        verbose_name="Challenge Date",
        orderable=False,
    )
    forfeit_date = tables.DateColumn(
        verbose_name="Forfeit Date",
        orderable=False,
    )
    void_date = tables.DateColumn(
        verbose_name="Void Date",
        orderable=False,
    )
    class Meta:
        model = Challenge
        exclude = ('id','played','play_date','g1_results','g2_results')
        attrs = {'class': 'table current','id':'current'}

class ChallengersTable(tables.Table):
    rank = tables.Column(orderable=False,)
    team = tables.LinkColumn(
        'team',
        args=[A('team')],
        verbose_name="Team",
        orderable=False,
    )
    challengerIn = tables.Column(
        verbose_name="Challenges In",
        orderable=False,
    )
    challengerOut = tables.Column(
        verbose_name="Challenges Out",
        orderable=False,
    )
    challengerStreak = tables.Column(
        verbose_name="Streak",
        orderable=False,
    )
    lastActive = tables.DateColumn(
        verbose_name="Last Active",
        orderable=False,
    )

    class Meta:
        attrs = {'class': 'table current'}
