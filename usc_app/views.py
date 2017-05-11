import json
import random
from datetime import date
from django.core.urlresolvers import reverse
from django.core.validators import ValidationError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.db.models import F
from django.db.models import Q
from django.shortcuts import render
from django_tables2 import RequestConfig
from django.utils.translation import gettext as _
from urllib.request import urlopen

from .models import *
from .table import *
from .forms import *
from .decorators import *

from bs4 import BeautifulSoup
from notify.signals import notify
from notify.models import Notification
from django_mobile import get_flavour
from collections import OrderedDict

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
    freeAgents = FreeAgent.objects.all()
    FA_table = FATable(freeAgents)
    FA_table.order_by = 'pk'
    return render(request, 'roster_table.html', {
        'count':queryset,
        'table': table,
        'players':players,
        'FA_table':FA_table,
    })
def team_page(request,team_name):
    team = Roster.objects.filter(team_name=team_name).first()
    rosters = Roster.objects.all().order_by('rank')
    # Stats Table
    stats = Stats.objects.filter(team=team_name)
    statsTable = StatsTable(stats)
    # Current Challenges Table
    currentChallenges = Challenge.objects.filter(Q(challenger=team.id)|Q(challenged=team.id)).filter(played=False)
    currentTable = CurrentChallenges(currentChallenges,empty_text="No current challenges!")
    # Challengers Table
    challengersTable = get_challengers(team_name)
    # Recent Games
    recentGames = get_recent_games(team)
    # Page template either for browser or mobile
    flavour = get_flavour()
    page = 'team_page.html' if flavour == 'full' else 'team_page_mobile.html'
    return render(request,page,{
        'team':team,
        'rosters':rosters, # for sidebar
        'statsTable':statsTable,
        'currentTable':currentTable,
        'challengersTable':challengersTable,
        'recentGames':recentGames,
        'rank':int(team.rank), # for pageheader coloring
    })
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
    challenger = Stats.objects.filter(team=request.user.team).first()
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
    challenger = Stats.objects.filter(team=request.user.team)
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
            challenger.update(challengeOut=F('challengeOut')+1)
            challenged.update(challengeIn=F('challengeIn')+1)
            notify.send(challengingTeam.captain.user, recipient=challengedTeam.captain.user, actor=challengingTeam,
                        verb='challenged you', nf_type='received_challenge')
            notify.send(challengedTeam.captain.user, recipient=challengingTeam.captain.user, actor=challengedTeam,
                        verb='challenged', nf_type='challenged_user')
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
def team_register(request):
    registered = False
    if request.method == 'POST':
        roster_form = RosterForm(request.POST,request.FILES)
        if roster_form.is_valid():
            roster = roster_form.save(commit=False)
            roster.abv = 'temp'
            rank = (Roster.objects.all().order_by('-rank')[0].rank)+1 if Roster.objects.count() > 0 else 1
            roster.rank = rank
            roster.firstActive=date.today()
            roster.daysActive = 0
            roster.save()
            registered = True
    else:
        roster_form = RosterForm()

    return render(request,
                  'team_register.html',
                  {'roster_form': roster_form,
                  'registered': registered,
                  'errors':roster_form.errors,
    })
def player_register(request):
    registered = False
    if request.method == 'POST':
        FA_form = FAForm(request.POST,request.FILES);
        if FA_form.is_valid():

            FA = FA_form.save(commit=False)
            user = User.objects.get(username=FA.name) if User.objects.filter(username=FA.name).exists() else User.objects.create(username=FA.name)
            FA.save()

            registered = True
        else:
            print(FA_form.errors)

    else:
        FA_form = FAForm()

    return render(request,'player_register.html',{
        'form': FA_form,
        'errors':FA_form.errors,
        'registered': registered,
    })
def results(request):
    queryset = Challenge.objects.all()
    table = ResultsTable(queryset)
    table.order_by = 'played'
    RequestConfig(request, paginate={
        'per_page': 40
    }).configure(table)

    return render(request, 'results.html', {
        'table':table
    })
def captain_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                if (user.username != 'admin'):
                    return HttpResponseRedirect(reverse('team',kwargs={'team_name':user.team}))
                else:
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
    return HttpResponseRedirect(reverse('login'))

def search(request):
    players = None
    teams = None
    total = 0
    if request.method == 'GET':
        query = request.GET.get('s',None)
        if query is not None and query is not '':
            players = Player.objects.filter(name__icontains=query)
            # teams = Roster.objects.filter(team_name__icontains=query,eligible=True)
            teams = Roster.objects.filter(team_name__icontains=query)
            total = players.count()+teams.count()
    return render(request,'search.html',{
        'players':players,
        'teams':teams,
        'query':query,
        'total':total
    })

def notifications(request):
    notifications = Notification.objects.filter(recipient=request.user)
    return render(request,'notifications.html',{
        'notifications':notifications,
    })

def test(request,team_name):
    team = Roster.objects.get(team_name=team_name)
    challenges = Challenge.objects.filter(Q(challenger=team.id)|Q(challenged=team.id)).filter(played=False)
    table = ResultsTable(challenges)
    return render(request,'test.html',{
        'table':table,
    })

@user_is_captain
def score_submit(request,challenge_id):
    challenge = Challenge.objects.filter(pk=challenge_id)
    # challenger_roster = Roster.objects.filter(team_name=challenge[0].challenger.team_name,eligible=True)
    # challenged_roster = Roster.objects.filter(team_name=challenge[0].challenged.team_name,eligible=True)
    challenger_roster = Roster.objects.filter(team_name=challenge[0].challenger.team_name)
    challenged_roster = Roster.objects.filter(team_name=challenge[0].challenged.team_name)
    challenger_stats = Stats.objects.filter(team=challenge[0].challenger.team_name)
    challenged_stats = Stats.objects.filter(team=challenge[0].challenged.team_name)
    submitted=False
    if request.method == 'POST':
        form = ScoresForm(request.POST)
        if form.is_valid():
            challenger_stats.update(GP=F('GP')+1)
            challenged_stats.update(GP=F('GP')+1)
            challenger_stats.update(challengeOut=F('challengeOut')-1)
            challenged_stats.update(challengeIn=F('challengeIn')-1)

            challenger_g1_score = form.cleaned_data['g1_t1_score']
            challenger_g2_score = form.cleaned_data['g2_t1_score']
            challenged_g1_score = form.cleaned_data['g1_t2_score']
            challenged_g2_score = form.cleaned_data['g2_t2_score']

            g1_results = Result(
                match_id=random.randint(1111111,9999999),
                team1=challenger_roster[0].abv,
                team2=challenged_roster[0].abv,
                score1=challenger_g1_score,
                score2=challenged_g1_score,
            )
            g2_results = Result(
                match_id=random.randint(1111111,9999999),
                team1=challenger_roster[0].abv,
                team2=challenged_roster[0].abv,
                score1=challenger_g2_score,
                score2=challenged_g2_score,
            )

            g1_results.save()
            g2_results.save()

            challenge.update(g1_results=g1_results)
            challenge.update(g2_results=g2_results)
            challenge.update(play_date=date.today())
            challenge.update(played=True)

            challenger_final_score = challenger_g1_score + challenger_g2_score
            challenged_final_score = challenged_g1_score + challenged_g2_score

            if challenger_final_score != challenged_final_score:
                if challenger_final_score > challenged_final_score:
                    winner_roster = challenger_roster
                    winner_stats = challenger_stats
                    loser_roster = challenged_roster
                    loser_stats = challenged_stats
                else:
                    loser_roster = challenger_roster
                    loser_stats = challenger_stats
                    winner_roster = challenged_roster
                    winner_stats = challenged_stats

                winner_stats.update(W=F('W')+1)
                loser_stats.update(L=F('L')+1)

                if winner_stats[0].streak < 0:
                    winner_stats.update(streak=1)
                else:
                    winner_stats.update(streak=F('streak')+1)
                if loser_stats[0].streak > 0:
                    loser_stats.update(streak=-1)
                else:
                    loser_stats.update(streak=F('streak')-1)

                wrank = winner_roster[0].rank
                lrank = loser_roster[0].rank

                changes = []
                if wrank > lrank:
                    for i in range((lrank+1),wrank):
                        changes.append(Roster.objects.filter(rank=i).first())
                    winner_roster.update(rank=lrank)
                    loser_roster.update(rank=lrank+1)
                    Roster.objects.filter(team_name__in=changes).update(rank=F('rank')+1)
                    Stats.objects.filter(team__in=changes).update(change=-1)
                winner_stats.update(change=(wrank-winner_roster[0].rank))
                loser_stats.update(change=(lrank-loser_roster[0].rank))

            else:
                challenger_stats.update(D=F('D')+1)
                challenged_stats.update(D=F('D')+1)

                challenger_stats.update(streak=0)
                challenged_stats.update(streak=0)

                challenger_stats.update(change=0)
                challenged_stats.update(change=0)


            submitted=True
            return render(request, 'score_submit.html',{
                'challenge':challenge[0],
                'submitted':submitted,
            })
        else:
            print(form.errors)
    else:
        form = ScoresForm()
    return render(request, 'score_submit.html', {
        'form': form,
        'challenge':challenge[0],
        'challenger':challenger_roster[0],
        'challenged':challenged_roster[0],
        'submitted':submitted,
    })

def forfeit(request, challenge_id):
    challenge = Challenge.objects.filter(pk=challenge_id)
    challenger = Stats.objects.filter(team=challenge.first().challenger)
    challenged = Stats.objects.filter(team=challenge.first().challenged)
    challenger.update(challengeOut=F('challengeOut')-1)
    challenged.update(challengeIn=F('challengeIn')-1)
    Stats.objects.filter(team=request.user.team).update(F=F('F')+1)
    if request.user.team == challenger.first().team:
        winner = Roster.objects.filter(team_name=challenged.first().team)
        loser = Roster.objects.filter(team_name=challenger.first().team)
    else:
        winner = Roster.objects.filter(team_name=challenger.first().team)
        loser = Roster.objects.filter(team_name=challenged.first().team)

    wrank = winner.first().rank
    lrank = loser.first().rank

    changes = []
    if wrank > lrank:
        if wrank-lrank<3:
            changes.append(Roster.objects.filter(rank=wrank+1).first())
            if wrank-lrank == 1:
                changes.append(Roster.objects.filter(rank=wrank+2).first())
            Roster.objects.filter(team_name__in=changes).update(rank=F('rank')-1)
        winner.update(rank=lrank)
        loser.update(rank=lrank+3)
        if wrank-lrank>3:
            Roster.objects.filter(rank=lrank+3).exclude(team_name=loser[0].team_name).update(rank=F('rank')+1)

    users = [winner.first().captain.user,loser.first().captain.user]
    notify.send(request.user, recipient_list=users, actor=Roster.objects.filter(team_name=request.user.team).first(),
                verb='forfeited.', target=challenge.first(), nf_type='forfeit')
    challenge.delete()

    return HttpResponseRedirect(reverse('team',kwargs={'team_name':request.user.team}))
@login_required
def drop_player(request,team_name,player_name):
    player = Player.objects.filter(name=player_name)
    User.objects.filter(username=player.first().name).update(team='')
    player.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def add_player(request):
    # player = Player.objects.filter(name=player_name) if Player.objects.filter(name=player_name).exists() else Player.objects.create(name=player_name)
    print('kek')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


########## HELPERS ###########
def get_challengers(team_name):
    team = Roster.objects.filter(team_name=team_name).first()
    challengers = []
    rosters = Roster.objects.all().order_by('rank')
    for roster in rosters:
        # Create list of challengers (teams 4 spots above current team)
        if team.rank - roster.rank <= 4 and team.rank - roster.rank > 0:
            challenger = OrderedDict()
            team_stats = Stats.objects.filter(team=roster.team_name).first()
            challenger["rank"]=roster.rank
            challenger["team"] = roster.team_name
            challenger["challengerIn"] = team_stats.challengeIn
            challenger["challengerOut"] = team_stats.challengeOut
            challenger["challengerStreak"] = team_stats.streak
            challenger["lastActive"] = team_stats.lastActive
            challengers.append(challenger)
    return ChallengersTable(challengers,empty_text = "You can't challenge anyone!")
def get_recent_games(team):
    if Challenge.objects.all().count():
        return Challenge.objects.filter(Q(challenged=team.id)|Q(challenger=team.id),played=True).order_by('-pk')[:2]
    else:
        return []
