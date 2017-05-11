from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from usc_app.models import *

register = template.Library()

@register.filter(name='is_captain')
def is_captain(user):
    return Captain.objects.filter(name=user.username).exists()

@register.filter(name='own_team')
def own_team(user,current_team):
    if is_captain(user):
        captain = Captain.objects.get(name=user.username)
        return current_team.captain == captain
    else:
        return False

@register.filter(name='can_challenge')
def can_challenge(user,current_team):
    try:
        userTeam = Roster.objects.get(team_name=user.team)
        userStats = Stats.objects.get(team=user.team)
        currentStats = Stats.objects.get(team=current_team.team_name)
        if currentStats in userTeam.getChallengers().values() and userStats.challengeOut < 2:
            return not Challenge.objects.filter(Q(challenger=userTeam.id)&Q(challenged=current_team.id)&Q(played=False)).exists()
        else:
            return False
    except ObjectDoesNotExist:
        return False
