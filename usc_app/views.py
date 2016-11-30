from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django_tables2 import RequestConfig
from django.shortcuts import get_object_or_404
from usc_app.models import *
from usc_app.table import *
from urllib.request import urlopen
from bs4 import BeautifulSoup
from urllib.request import urlopen
import json
import operator
from base64 import decodestring
from django.db.models import F
from django.forms import modelformset_factory
from .forms import ChallengeForm

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
    challenges = Challenge.objects.filter(challenger=team.id)
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
        'rank':rank, # for page header
        'challenges':challenges
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
def challenge(request):
    if request.method == 'POST': # If the form has been submitted...
        form = ChallengeForm(request.POST) # A form bound to the POST data
        if form.is_valid():
            form.save()
    else:
        form = ChallengeForm()
    return render(request, 'challenge.html', {'form': form})
def test(request):
    teams = Roster.objects.values_list('abv', flat=True)
    # test = ['Red','Blue']
    tp = 'https://tagpro.eu/?matches&page=7'
    page = urlopen(tp)
    soup = BeautifulSoup(page,'lxml')
    rows = soup.find_all('tr')
    games = {}
    test = None
    for row in rows:
        try:
            team1 = row.find_all('td')[4]
            team2 = row.find_all('td')[5]

        except IndexError:
            continue

        if team1.find('a'):
            match_id = row.find_all('td')[0].get_text()
            team1 = team1.find('a').get_text()
            team2 = team2.find('a').get_text()
            match_map = row.find_all('td')[3].get_text()
            score1 = row.find_all('td')[9].get_text()
            score2 = row.find_all('td')[10].get_text()
            if int(score2) > int(score1):
                winner = [team2]
                loser = team1
                winnerScore = score2
                loserScore = score1
            else:
                winner = [team1]
                loser = team2
                winnerScore = score1
                loserScore = score2
            if winner == ['Blue']:
                winner = ['Blu']
            if loser == 'Blue':
                loser = 'Blu'
            games[match_id] = winner
            games[match_id].append(loser)
            games[match_id].append(winnerScore)
            games[match_id].append(loserScore)
            games[match_id].append(match_map)
#Roster.objects.filter(abv=team1).update(rank = F('rank')+1)
    # for game,teams in contents.items():
    #     tp = "https://tagpro.eu/?download=" + game[1:]
    #     data = json.loads(urlopen(tp).read().decode('utf-8'))
    #     games[game].append(data['teams'][0]['score'])
    #     games[game].append(data['teams'][1]['score'])
    return render(request, 'test.html',{
        'soup':games, # {'match_id':['Team1','Team2','Score1','Score2','Map']}
        'test':teams,
    })
