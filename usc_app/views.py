import json
import random
from datetime import date
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.db.models import F
from django.db.models import Q
from django.shortcuts import render
from django_tables2 import RequestConfig
from django.utils.translation import gettext as _

from .models import *
from .table import *
from .forms import *
from .decorators import *
from .score_handler import *

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
    team = Roster.objects.get(team_name=team_name)
    rosters = Roster.objects.all().order_by('rank')
    # Stats Table
    stats = Stats.objects.filter(team=team_name)
    statsTable = StatsTable(stats)
    # Current Challenges Table
    currentChallenges = Challenge.objects.filter(Q(challenger=team.id)|Q(challenged=team.id)).filter(played=False)
    currentTable = CurrentChallenges(currentChallenges,empty_text="No current challenges!")
    # Challengers Table
    challengersTable = get_challengers(team)
    # Recent Games
    recentGames = get_recent_games(team)
    # Page template either for browser or mobile
    flavour = get_flavour()
    page = 'team_page.html' if flavour == 'full' else 'team_page_mobile.html'
    return render(request,page,{
        'team':team,
        'stats':stats,
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
def challenge(request,team_id):
    user = request.user
    if request.method == 'POST': # If the form has been submitted...
        form = ChallengeForm(request.POST,request=request,team_id=team_id) # A form bound to the POST data
        if form.is_valid():
            challenge = process_challenge(form,user)
            return render(request, 'challenge_success.html',{
                'challenge':challenge,
            })
    else:
        if cannot_challenge(user):
            return render(request, 'redirect.html', {
                'title': 'Invalid Challenge',
                'content': 'You already have 2 challenges out!',
                'url_arg': 'index',
                'url_text': 'Back to homepage',
            })
        form = ChallengeForm(request=request,team_id=team_id)
    return render(request, 'challenge.html', {
        'form': form,
        'team_id':team_id
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
            teams = Roster.objects.filter(team_name__icontains=query)
            total = players.count()+teams.count()
    return render(request,'search.html',{
        'players':players,
        'teams':teams,
        'query':query,
        'total':total
    })

@user_is_captain
def notifications(request):
    notifications = Notification.objects.filter(recipient=request.user)
    return render(request,'notifications.html',{
        'notifications':notifications,
    })

@user_is_captain
def score_submit(request,challenge_id):
    user = request.user
    challenge = Challenge.objects.get(pk=challenge_id)
    challenge_stats = Challenge.objects.filter(pk=challenge_id)
    if request.method == 'POST':
        form = ScoresForm(request.POST)
        if form.is_valid():
            prepared_games = prepare_games(challenge,form)
            g1 = prepared_games['g1']
            g2 = prepared_games['g2']
            challenge_stats.update(g1_submitted=g1)
            challenge_stats.update(g2_submitted=g2)
            challenge_stats.update(submitted_by=user)
            return HttpResponseRedirect(reverse('submit',kwargs={'challenge_id':challenge_id}))
    else:
        form = ScoresForm()
    return render(request, 'score_submit.html', {
        'challenge':challenge,
        'form': form,
        'user':user,
    })
@user_is_captain
def accept_score(request,challenge_id,g1_id,g2_id):
    user = request.user
    g1 = Result.objects.get(pk=g1_id)
    g2 = Result.objects.get(pk=g2_id)
    final_score = finialize_game(g1,g2)
    update_challenge(challenge_id,g1,g2,final_score)
    return HttpResponseRedirect(reverse('team',kwargs={'team_name':user.team}))
@user_is_captain
def reject_score(request,challenge_id):
    user = request.user
    challenge_stats = Challenge.objects.filter(pk=challenge_id)
    challenge_stats.update(g1_submitted=None)
    challenge_stats.update(g2_submitted=None)
    return HttpResponseRedirect(reverse('team',kwargs={'team_name':user.team}))

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
def add_player(request,team_name,field,player_name):
    team = Roster.objects.get(team_name=team_name)
    try:
        user = User.objects.get(username=player_name)
        assert user.team == ''
        player = Player.objects.create(name=player_name,user=user)
        place_player(player,team,field)
        user.update(team=team_name)
    except ObjectDoesNotExist:
        user = User.objects.create(username=player_name,team=team_name)
        player = Player.objects.create(name=player_name,user=user)
        place_player(player,team,field)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def drop_player(request,team_name,player_name):
    User.objects.get(username=player_name).delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def check_username(request):
    name = request.GET.get('name', None)
    data = {
        'is_taken': Player.objects.filter(name__iexact=name).exists()
    }
    return JsonResponse(data)

########## HELPERS ###########
def get_challengers(team):
    challengers = []
    rosters = Roster.objects.all().order_by('rank')
    for roster in rosters:
        # Create list of challengers (teams 4 spots above current team)
        if team.rank - roster.rank <= 4 and team.rank - roster.rank > 0:
            challenger = OrderedDict()
            team_stats = Stats.objects.get(team=roster.team_name)
            challenger["rank"]=roster.rank
            challenger["team"] = roster.team_name
            challenger["challengerIn"] = team_stats.get_challengeIn
            challenger["challengerOut"] = team_stats.get_challengeOut
            challenger["challengerStreak"] = team_stats.streak
            challenger["lastActive"] = team_stats.lastActive
            challengers.append(challenger)
    return ChallengersTable(challengers,empty_text = "You can't challenge anyone!")
def get_recent_games(team):
    if Challenge.objects.all().count():
        return Challenge.objects.filter(Q(challenged=team.id)|Q(challenger=team.id),played=True).order_by('-pk')[:2]
    else:
        return []
def place_player(player,team,field):
    if field == 'co_captain':
        team.co_captain = player
    elif field == 'member1':
        team.member1 = player
    elif field == 'member2':
        team.member2 = player
    elif field == 'member3':
        team.member3 = player
    elif field == 'member4':
        team.member4 = player
    elif field == 'member5':
        team.member5 = player
    else:
        team.member6 = player
    team.save()

def cannot_challenge(user):
    # check to see if user cannot challenge (2 challenges out already)
    return Stats.objects.get(team=user.team).get_challengeOut() > 1

def process_challenge(form,user):
    # process challenge form after validation, send notifications
    challenge = form.save(commit=False)
    challenge.challenger = Roster.objects.filter(team_name=user.team).first()
    challenge.save()
    notify.send(user, recipient=challenge.challenged.captain.user, actor=challenge.challenger,
                verb='challenged you', nf_type='received_challenge')
    notify.send(challenge.challenged.captain.user, recipient=user, actor=challenge.challenged,
                verb='challenged', nf_type='challenged_user')
    return challenge
