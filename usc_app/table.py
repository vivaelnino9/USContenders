import django_tables2 as tables
from usc_app.models import *
from django.core.urlresolvers import reverse
from django_tables2.utils import A

class RosterTable(tables.Table):
    team_name = tables.LinkColumn('team',args=[A('team_name')], verbose_name="Team",)
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
            'id': lambda record: 'R' + str(record.rank)
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
    GP = tables.Column(orderable=False,)
    W = tables.Column(orderable=False,)
    L = tables.Column(orderable=False,)
    D = tables.Column(orderable=False,)
    F = tables.Column(orderable=False,)
    CF = tables.Column(orderable=False,)
    CA = tables.Column(orderable=False,)
    CD = tables.Column(orderable=False,)
    CDperG = tables.Column(orderable=False,verbose_name="CD/G")
    class Meta:
        model = Stats
        exclude = ('id','lastActive','team','abv')
        attrs = {
            'class': 'subTeamName',
            'align': 'center',
            'th': {
                'id' : 'statTableHeader'
            }
        }
class ResultsTable(tables.Table):
    challenger = tables.LinkColumn('team',args=[A('challenger')])
    challenged = tables.LinkColumn('team',args=[A('challenged')])
    g1_results = tables.LinkColumn('game_results',args=[A('g1_results')],orderable=False)
    g2_results = tables.LinkColumn('game_results',args=[A('g2_results')],orderable=False)
    class Meta:
        model = Challenge
        exclude = ('id',)
        attrs = {'class': 'table'}
        row_attrs = {
            'id': lambda record: 'P' + str(record.played)
        }
