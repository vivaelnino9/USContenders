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
    queryset = Roster.objects.all()
    table = RosterTable(queryset)
    players = Player.objects.all()
    table.order_by = 'rank'
    RequestConfig(request, paginate={
        'per_page': 38
    }).configure(table)
    return render(request, 'roster_table.html', {
        'table': table,
        'players':players,
    })
def team_page(request,team_name):
    rosters = Roster.objects.all().order_by('rank')
    team = Roster.objects.filter(team=team_name).first()
    stats = Stats.objects.filter(team=team_name).first()
    queryset = Stats.objects.filter(team=team.team)
    table = StatsTable(queryset)
    challengers = {}
    rank = int(team.rank)
    for roster in rosters:
        # Create list of challengers (teams 4 spots above current team)
        if rank - roster.rank <= 4 and rank - roster.rank > 0:
            challengers[roster.rank]= get_object_or_404(Stats, team=roster.team)
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
    rosters = Roster.objects.all().order_by('rank')
    player = Player.objects.filter(name=player_name).first()
    rank = player.roster.rank
    return render(request,'player_page.html',{
        'rosters':rosters,
        'player':player,
        'rank':rank,
    })
