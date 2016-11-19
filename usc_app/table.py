import django_tables2 as tables
from usc_app.models import *
from django.core.urlresolvers import reverse
from django_tables2.utils import A

class RosterTable(tables.Table):
    team = tables.LinkColumn('team',args=[A('team')], verbose_name="Team",)
    rank = tables.Column(verbose_name="Rank")
    captain = tables.Column(orderable=False, verbose_name="Captain")
    co_captain = tables.Column(
        orderable=False,
        verbose_name="Co-Captain"
        # default="",
    )
    member1 = tables.Column(
        orderable=False,
        verbose_name="Member",
        # default="",
    )
    member2 = tables.Column(
        orderable=False,
        verbose_name="Member",
        # default="",
    )
    member3 = tables.Column(
        orderable=False,
        verbose_name="Member",
        # default="",
    )
    member4 = tables.Column(
        orderable=False,
        verbose_name="Member",
        # default="",
    )
    member5 = tables.Column(
        orderable=False,
        verbose_name="Member",
        # default="",
    )
    member6 = tables.Column(
        orderable=False,
        verbose_name="Member",
        # default="",
    )
    server = tables.Column(verbose_name="Server")
    class Meta:
        model = TeamRoster
        exclude = ('id','firstActive','daysActive','logo')
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
        model = TeamStats
        exclude = ('id','lastActive','team')
        attrs = {
            'class': 'subTeamName',
            'align': 'center',
            'th': {
                'id' : 'statTableHeader'
            }
        }
