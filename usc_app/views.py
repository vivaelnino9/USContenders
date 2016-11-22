from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django_tables2 import RequestConfig
from django.shortcuts import get_object_or_404
from usc_app.models import *
from usc_app.table import *
import operator

def index(request):
    return render(request, 'index.html')

def roster_table(request):
    queryset = TeamRoster.objects.all()
    table = RosterTable(queryset)
    table.order_by = 'rank'
    RequestConfig(request, paginate={
        'per_page': 38
    }).configure(table)
    return render(request, 'roster_table.html', {'table': table,})
def team_page(request,team_name):
    rosters = TeamRoster.objects.all().order_by('rank')
    # team = get_object_or_404(TeamRoster,team=team_name)
    # stats = get_object_or_404(TeamStats,team=team_name)
    team = TeamRoster.objects.filter(team=team_name).first()
    stats = TeamStats.objects.filter(team=team_name).first()
    queryset = TeamStats.objects.filter(team=team.team)
    table = StatsTable(queryset)
    challengers = {}
    rank = int(team.rank)
    for roster in rosters:
        # Create list of challengers (teams 4 spots above current team)
        if rank - roster.rank <= 4 and rank - roster.rank > 0:
            challengers[roster.rank]= get_object_or_404(TeamStats, team=roster.team)
    sorted_challengers = sorted(challengers.items(), key=operator.itemgetter(0)) #Sort challengers list by key(rank)
    return render(request,'team_page.html',{
        'team':team, # for team page
        'rosters':rosters, # for side bar
        'table':table, # for team stats under team name
        'stats':stats, # for team stats highlighting
        'challengers':sorted_challengers, # for teams to challenge
        'rank':rank # for page header
    });
def player_page(request,player_name):
    rosters = TeamRoster.objects.all().order_by('rank')
    return render(request,'player_page.html',{
        'rosters':rosters,
    })
