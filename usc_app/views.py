import json
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.db.models import F
from django.shortcuts import render
from django_tables2 import RequestConfig
from urllib.request import urlopen

from .models import *
from .table import *
from .forms import *

from bs4 import BeautifulSoup
from django.core.validators import ValidationError
from django.utils.translation import gettext as _

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
    team = Roster.objects.filter(team_name=team_name).first()
    userTeam = Roster.objects.filter(team_name=request.user.first_name).first()
    own_page = False
    if userTeam.team_name == team_name:
        own_page = True
    challenged = False
    if Challenge.objects.filter(challenger=userTeam.id).filter(challenged=team.id).filter(played=False):
        challenged = True
    stats = Stats.objects.filter(team=team_name).first()
    userStats = Stats.objects.filter(team=userTeam.team_name).first()
    queryset = Stats.objects.filter(team=team_name)
    table = StatsTable(queryset)
    canChallenge = team.getChallengers
    challenges = Challenge.objects.filter(challenger=team.id)
    rank = int(team.rank)
    return render(request,'team_page.html',{
        'rosters':rosters, # for side bar
        'team':team, # for team page
        'userTeam':userTeam, # team of user visiting page
        'own_page':own_page, # true if user visiting own page
        'challenged':challenged, # true if user has challenge against team_page
        'stats':stats, # for team stats highlighting
        'userStats':userStats, # for userTeam stats
        'table':table, # for team stats under team name
        'canChallenge':canChallenge, # for teams to challenge
        'challenges':challenges,  # list of challenges team has out
        'rank':rank, # for page header
    });
def player_page(request,player_name,team_name):
    rosters = Roster.objects.all().order_by('rank')
    player = Player.objects.filter(name=player_name).first()
    captain = Captain.objects.filter(name=player_name).first()
    team = Roster.objects.filter(team_name=team_name).first()
    rank = team.rank
    return render(request,'player_page.html',{
        'rosters':rosters,
        'player':player,
        'captain':captain,
        'team':team.team_name,
        'rank':rank,
    })
@login_required
def challenge(request):
    challenger = Stats.objects.filter(team=request.user.first_name).first()
    challengeOut = challenger.challengeOut
    error = (challengeOut + 1) > 2
    if request.method == 'POST': # If the form has been submitted...
        form = ChallengeForm(request.POST,request=request) # A form bound to the POST data
        if form.is_valid() and not error:
            challenge= form.save(commit=False)
            captain = Captain.objects.filter(name=request.user.username).first()
            challenge.challenger = Roster.objects.filter(captain=captain.id).first()
            challenge.save()
            return render(request, 'challenge_success.html',{
                'challenge':challenge,
            })
        else:
            print(form.errors)
    else:
        if error:
            return render(request, 'redirect.html', {
                'title': 'Invalid Challenge',
                'content': 'You already have 2 challenges out!',
                'url_arg': 'index',
                'url_text': 'Back to homepage',
        })
        form = ChallengeForm(request=request)
    return render(request, 'challenge.html', {
        'form': form,
    })
@login_required
def challenge_with_arg(request,team_challenged):
    challenger = Stats.objects.filter(team=request.user.first_name)
    challenged = Stats.objects.filter(team=team_challenged)
    challengingTeam = Roster.objects.filter(team_name=challenger[0].team).first()
    challengedTeam = Roster.objects.filter(team_name=team_challenged).first()
    existingChallenge = Challenge.objects.filter(challenger=challengingTeam.id).filter(challenged=challengedTeam.id).filter(played=False)
    challengeOut = challenger[0].challengeOut
    error = (challengeOut + 1) > 2
    if request.method == 'POST': # If the form has been submitted...
        form = ChallengeArgForm(request.POST) # A form bound to the POST data
        if form.is_valid() and not error and not existingChallenge:
            challenge= form.save(commit=False)
            challenge.challenger = challengingTeam
            challenge.challenged = challengedTeam
            challenge.save()
            #Roster.objects.filter(abv=team1).update(rank = F('rank')+1)
            challenger.update(challengeOut=F('challengeOut')+1)
            challenged.update(challengeIn=F('challengeIn')+1)
            return render(request, 'challenge_success.html',{
                'challenge':challenge,
            })
        else:
            if existingChallenge:
                return render(request, 'redirect.html', {
                    'title': 'Invalid Challenge',
                    'content': 'You already have a challenge out against that team!',
                    'url_arg': 'index',
                    'url_text': 'Back to homepage',
            })
            else:
                print(form.errors)
    else:
        if error:
            return render(request, 'redirect.html', {
                'title': 'Invalid Challenge',
                'content': 'You already have 2 challenges out!',
                'url_arg': 'index',
                'url_text': 'Back to homepage',
        })
        form = ChallengeArgForm()
    return render(request, 'challenge.html', {
        'form': form,
        'challenger':challenger[0],
        'challenged':challenged[0],
    })
@login_required
def challenge_success(request):
    return render(request, 'challenge_success.html', {})
def captain_register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        captain_form = CaptainForm(data=request.POST);

        if user_form.is_valid() and captain_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)

            captain = captain_form.save(commit=False)
            captain.user = user
            captain.name = user.username

            user.first_name = captain.team.team_name

            user.save()
            captain.save()

            Roster.objects.filter(team_name=captain.team).update(captain=captain)
            registered = True
        else:
            print(user_form.errors, captain_form.errors)

    else:
        user_form = UserForm()
        captain_form = CaptainForm()

    return render(request,
                  'register.html',
                  {'user_form': user_form,
                  'captain_form': captain_form,
                  'registered': registered,
                  'errors':user_form.errors,
    })
def results(request):
    queryset = Challenge.objects.all()
    table = ResultsTable(queryset)
    table.order_by = 'played'
    RequestConfig(request, paginate={
        'per_page': 40
    }).configure(table)


    tp = 'https://tagpro.eu/?matches'
    page = urlopen(tp)
    soup = BeautifulSoup(page,'lxml')
    rows = soup.find_all('tr')
    result = None
    for row in rows:
        try:
            team1 = row.find_all('td')[4]
            team2 = row.find_all('td')[5]

        except IndexError:
            continue

        if team1.find('a'):
            for challenge in Challenge.objects.all():
                challenge_formatted = challenge.format()
                if challenge_formatted[0] == team1.get_text() and challenge_formatted[1] == team2.get_text() or challenge_formatted[0] == team2.get_text() and challenge_formatted[1] == team1.get_text():
                    match_id = row.find_all('td')[0].get_text()
                    if not Result.objects.filter(match_id=match_id) and not challenge.played:
                        server = row.find_all('td')[1].get_text()
                        team1 = team1.find('a').get_text()
                        team2 = team2.find('a').get_text()
                        match_map = row.find_all('td')[3].get_text()
                        duration = row.find_all('td')[8].get_text()
                        score1 = row.find_all('td')[9].get_text()
                        score2 = row.find_all('td')[10].get_text()
                        result = Result(
                            match_id=match_id,server=server,duration=duration,
                            team1=team1,team2=team2,score1=score1,score2=score2
                        )
                        result.save()
                        if not challenge.g2_results:
                            Challenge.objects.filter(challenger=challenge.challenger).update(g2_results=result)
                        elif not challenge.g1_results:
                            Challenge.objects.filter(challenger=challenge.challenger).update(g1_results=result)
                            Challenge.objects.filter(challenger=challenge.challenger).update(played=True)
                        else:
                            pass
    return render(request, 'results.html', {
        'table': table,
    })
def captain_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('rosters'))
            else:
                return render(request, 'redirect.html', {
                    'title': 'Account Disabled',
                    'heading': 'Banned',
                    'content': 'Your account has been disabled. Contact an administrator.',
                    'url_arg': 'index',
                    'url_text': 'Back to homepage'
            })

        else:
            return render(request, 'redirect.html', {
                'title': 'Invalid Login',
                'heading': 'Incorrect Login',
                'content': 'Invalid login details for: {0}'.format(username),
                'url_arg': 'login',
                'url_text': 'Back to login'
            })
    else:
        return render(request, 'login.html', {})
def captain_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))
def game_results(request,match_id):
    result = Result.objects.filter(match_id=match_id).first()
#Roster.objects.filter(abv=team1).update(rank = F('rank')+1)
    # for game,teams in contents.items():
    #     tp = "https://tagpro.eu/?download=" + game[1:]
    #     data = json.loads(urlopen(tp).read().decode('utf-8'))
    #     games[game].append(data['teams'][0]['score'])
    #     games[game].append(data['teams'][1]['score'])
    return render(request, 'game_results.html',{
        'result':result,
    })
