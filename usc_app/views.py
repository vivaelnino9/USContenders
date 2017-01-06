import json
from datetime import date
from django.core.urlresolvers import reverse
from django.core.validators import ValidationError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.db.models import F
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
    return render(request, 'roster_table.html', {
        'count':queryset,
        'table': table,
        'players':players,
    })
def team_page(request,team_name):
    currentUser = request.user
    team = Roster.objects.filter(team_name=team_name).first()
    rosters = Roster.objects.all().order_by('rank')
    currentChallengesOut = Challenge.objects.filter(challenger=team.id).filter(played=False)
    currentChallengesIn = Challenge.objects.filter(challenged=team.id).filter(played=False)
    stats = Stats.objects.filter(team=team_name)
    table = StatsTable(stats)
    rank = int(team.rank)
    recentGames = []
    challengersList = team.getChallengers
    if Challenge.objects.count() > 0:
        for challenge in Challenge.objects.all()[:2]:
            if (challenge.challenger.id == team.id or challenge.challenged.id == team.id) and challenge.played == True:
                recentGames.append(challenge)
    if Captain.objects.filter(name=currentUser.username) and not currentUser.first_name == team_name:
        # If current user is captain, but is viewing another team page
        userTeam = Roster.objects.filter(team_name=currentUser.first_name).first()
        userStats = Stats.objects.filter(team=userTeam.team_name).first()
        canChallenge = False
        for rank,roster in userTeam.getChallengers().items():
            if roster.challengeIn < 2 or userStats.challengeOut < 2 or not Challenge.objects.filter(challenger=userTeam.id).filter(challenged=team.id).filter(played=False):
                canChallenge = True
        return render(request,'team_page.html',{
            'team':team,
            'rosters':rosters,
            'currentChallengesOut':currentChallengesOut,
            'currentChallengesIn':currentChallengesIn,
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
            'currentChallengesOut':currentChallengesOut,
            'currentChallengesIn':currentChallengesIn,
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
            notify.send(challengedTeam.captain.user, recipient=challengedTeam.captain.user, actor=challengingTeam,
                        verb='challenged you', nf_type='challenged_user')
            notify.send(challengingTeam.captain.user, recipient=challengingTeam.captain.user, actor=challengingTeam,
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
def captain_register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        captain_form = CaptainForm(request.POST,request.FILES);

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

    if Challenge.objects.filter(played=False).exists():
        tp = 'https://tagpro.eu/?matches'
        page = urlopen(tp)
        soup = BeautifulSoup(page,'lxml')
        rows = soup.find_all('tr')
        result = None
        for row in reversed(rows):
            try:
                team1 = row.find_all('td')[4]
                team2 = row.find_all('td')[5]

            except IndexError:
                continue

            # if team1.find('a'):
            if not team1.get_text() == 'public':
                for challenge in Challenge.objects.all():
                    challenge_formatted = challenge.format()
                    if ((challenge_formatted[0] == team1.get_text() and challenge_formatted[1]) == team2.get_text() or (challenge_formatted[0] == team2.get_text() and challenge_formatted[1] == team1.get_text())) and not challenge.played:
                        match_id = int(row.find_all('td')[0].get_text()[1:])
                        if not Result.objects.filter(match_id=match_id) and not challenge.played:
                            team1 = team1.get_text()
                            team2 = team2.get_text()
                            score1 = row.find_all('td')[9].get_text()
                            score2 = row.find_all('td')[10].get_text()
                            challenger = Stats.objects.filter(abv=challenge.challenger.abv)
                            challenged = Stats.objects.filter(abv=challenge.challenged.abv)
                            result = Result(
                                match_id=match_id,team1=team1,team2=team2,
                                score1=score1,score2=score2
                            )
                            result.save()
                            t1 = Stats.objects.filter(abv=str(team1))
                            t2 = Stats.objects.filter(abv=str(team2))
                            c = Challenge.objects.filter(challenger=challenge.challenger).exclude(played=True)
                            if not challenge.g1_results:
                                c.update(g1_results=result)
                            elif not challenge.g2_results:
                                c.update(g2_results=result)
                                c.update(play_date=date.today())
                                c.update(played=True)
                                challenger.update(challengeOut=F('challengeOut')-1)
                                challenged.update(challengeIn=F('challengeIn')-1)
                                t1.update(GP=F('GP')+1)
                                t2.update(GP=F('GP')+1)
                                score1 = int(score1)
                                score2 = int(score2)
                                if challenge.g1_results.team1 == team2:
                                    t1final = challenge.g1_results.score1 + score2
                                    t2final = challenge.g1_results.score2 + score1
                                else:
                                    t1final = challenge.g1_results.score1 + score1
                                    t2final = challenge.g1_results.score2 + score2
                                t1 = Stats.objects.filter(abv=challenge.g1_results.team1)
                                t2 = Stats.objects.filter(abv=challenge.g1_results.team2)
                                if t1final > t2final:
                                    winner = t1
                                    loser = t2
                                elif t2final > t1final:
                                    winner = t2
                                    loser = t1
                                else:
                                    t1.update(D=F('D')+1)
                                    t2.update(D=F('D')+1)
                                    t1.update(streak=0)
                                    t2.update(streak=0)

                                winner.update(W=F('W')+1)
                                loser.update(L=F('L')+1)

                                if winner[0].streak < 0:
                                    winner.update(streak=1)
                                else:
                                    winner.update(streak=F('streak')+1)
                                if loser[0].streak > 0:
                                    loser.update(streak=-1)
                                else:
                                    loser.update(streak=F('streak')-1)

                                win = Roster.objects.filter(team_name=winner[0].team)
                                los = Roster.objects.filter(team_name=loser[0].team)

                                wrank = win[0].rank
                                lrank = los[0].rank

                                changes = []
                                if wrank > lrank:
                                    for i in range((lrank+1),wrank):
                                        changes.append(Roster.objects.filter(rank=i).first())
                                    win.update(rank=lrank)
                                    los.update(rank=lrank+1)
                                    Roster.objects.filter(team_name__in=changes).update(rank=F('rank')+1)

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
    # user = User.objects.get(username='Rattpack')
    # notify.send(request.user, recipient=request.user, actor=user,
    #             verb='followed you', nf_type='followed_user')
    return render(request,'notifications.html',{
        'notifications':notifications,
    })
