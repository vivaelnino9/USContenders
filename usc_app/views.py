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

from bs4 import BeautifulSoup
from notify.signals import notify
from notify.models import Notification

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
    currentUser = request.user
    team = Roster.objects.filter(team_name=team_name).first()
    rosters = Roster.objects.all().order_by('rank')
    currentChallenges = Challenge.objects.filter(Q(challenger=team.id)|Q(challenged=team.id)).filter(played=False)
    stats = Stats.objects.filter(team=team_name)
    table = StatsTable(stats)
    rank = int(team.rank)
    if Challenge.objects.all().count():
        recentGames = Challenge.objects.filter(Q(challenged=team.id)|Q(challenger=team.id),played=True).order_by('-pk')[:2]
    else:
        recentGames = []
    challengersList = team.getChallengers
    if Captain.objects.filter(name=currentUser.username) and not currentUser.team == team_name:
        # If current user is captain, but is viewing another team page
        userTeam = Roster.objects.filter(team_name=currentUser.team).first()
        userStats = Stats.objects.filter(team=userTeam.team_name).first()
        canChallenge = False
        for rank,roster in userTeam.getChallengers().items():
            if roster.team == team.team_name:
                if roster.challengeIn < 2 and userStats.challengeOut < 2:
                    if not Challenge.objects.filter(Q(challenger=userTeam.id)&Q(challenged=team.id)&Q(played=False)):
                        canChallenge = True
        return render(request,'team_page.html',{
            'team':team,
            'rosters':rosters,
            'currentChallenges':currentChallenges,
            'stats':stats.first(),
            'table':table,
            'rank':rank,
            'recentGames':recentGames,
            'challengersList':challengersList,
            'userTeam':userTeam,
            'canChallenge':canChallenge,
        })
    else:
        return render(request,'team_page.html',{
            'team':team,
            'rosters':rosters,
            'currentChallenges':currentChallenges,
            'stats':stats.first(),
            'table':table,
            'rank':rank,
            'recentGames':recentGames,
            'challengersList':challengersList,
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
            #Roster.objects.filter(abv=team1).update(rank = F('rank')+1)
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
def roster_register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        roster_form = RosterForm(request.POST,request.FILES);

        if user_form.is_valid() and captain_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)

            captain = captain_form.save(commit=False)
            captain.user = user
            captain.name = user.username

            # user.team = captain.team.team_name

            user.save()
            captain.save()

            Roster.objects.filter(team_name=captain.team).update(captain=captain)
            registered = True
        else:
            print(user_form.errors, roster_form.errors)

    else:
        user_form = UserForm()
        roster_form = RosterForm()

    return render(request,
                  'register.html',
                  {'user_form': user_form,
                  'roster_form': roster_form,
                  'registered': registered,
                  'errors':user_form.errors,
    })
def player_register(request):
    registered = False
    if request.method == 'POST':
        FA_form = FAForm(request.POST,request.FILES);
        if FA_form.is_valid():

            FA = FA_form.save(commit=False)
            user = User.objects.create(username=FA.name)
            FA.user = user

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
            players = User.objects.filter(username__icontains=query)
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

def score_submit(request,challenge_id):
    challenge = Challenge.objects.filter(pk=challenge_id)
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
