from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from usc_app.models import *

register = template.Library()

# *** current team refers to the team_page that the user is on ***

@register.filter(name='is_captain')
# checks if user is a captain
def is_captain(user):
    return Captain.objects.filter(name=user.username).exists()

@register.filter(name='own_team')
# checks if user is the captain of the current team
def own_team(user,current_team):
    if is_captain(user):
        captain = Captain.objects.get(name=user.username)
        return current_team.captain == captain
    else:
        return False

@register.filter(name='can_challenge')
# checks if users team can challenge the current team, checking if there is an
# existing challenge or if the current team already has 2 challenges in
def can_challenge(user,current_team):
    try:
        userTeam = Roster.objects.get(team_name=user.team)
        userStats = Stats.objects.get(team=user.team)
        currentStats = Stats.objects.get(team=current_team.team_name)
        if currentStats in userTeam.getChallengers().values() and userStats.get_challengeOut() < 2:
            return not Challenge.objects.filter(Q(challenger=userTeam.id)&Q(challenged=current_team.id)&Q(played=False)).exists()
        else:
            return False
    except ObjectDoesNotExist:
        return False

@register.filter(name='can_remove_player')
# gets the number of members on roster (including co-captain) and returns
# True if more than 4 players, False if not. Teams can't have less than 4.
def can_remove_player(team):
    players = []
    for field in Roster._meta.fields:
        if field.get_internal_type() == 'ForeignKey':
            if field.rel.to==Player:
                player = getattr(team,field.name)
                if player is not None: players.append(player)
    return len(players) > 4
