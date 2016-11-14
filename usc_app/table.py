import django_tables2 as tables
from usc_app.models import *
from django.core.urlresolvers import reverse
from django_tables2.utils import A

class RosterTable(tables.Table):
    id = tables.Column(orderable=False)
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
    active = tables.Column(orderable=False, verbose_name="Active")
    server = tables.Column(verbose_name="Server")
    class Meta:
        model = Roster
        exclude = ('id', )
        attrs = {'class': 'table'}
        row_attrs = {
            'id': lambda record: 'R' + str(record.rank)
        }
