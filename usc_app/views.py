from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django_tables2 import RequestConfig
from django.shortcuts import get_object_or_404
from usc_app.models import *
from usc_app.table import *

def index(request):
    return render(request, 'index.html')

def roster_table(request):
    queryset = Roster.objects.all()
    table = RosterTable(queryset)
    table.order_by = 'rank'
    RequestConfig(request, paginate={
        'per_page': 38
    }).configure(table)
    return render(request, 'roster_table.html', {'table': table,})
def team_page(request,team_name):
    baseurl = request.get_full_path()
    rosters = Roster.objects.all().order_by('rank')
    team = get_object_or_404(Roster, team=team_name)
    test = []
    rank = int(team.rank)
    count = 0
    for roster in rosters:
        if rank - roster.rank <= 4 and rank - roster. rank > 0:
            test.append(get_object_or_404(Roster, team=roster.team))
        count+=1
    # queryset = Roster.objects.all()
    return render_to_response('team_page.html',{
        'team':team,
        'baseurl': baseurl,
        'rosters':rosters,
        'test':test,
        'rank':rank
    });
