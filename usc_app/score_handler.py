import random
from datetime import date
from django.db.models import F

from .models import *


def get_final_score(g1,g2):
    # determine final score from g1 and g2, if draw update stats accordingly
    team1 = g1.team1
    team2 = g1.team2
    # ** make sure these are team_names not abv's **
    team1_score = g1.team1_score + g2.team1_score if team1 == g2.team1 else g1.team1_score + g2.team2_score
    team2_score = g1.team2_score + g2.team2_score if team2 == g2.team2 else g1.team2_score + g2.team1_score
    draw = team1_score == team2_score
    if draw:
        winner=loser=None
        winner_score=loser_score=0
        update_draw_stats(team1,team2,team1_score,team2_score)
    else:
        if team1_score > team2_score:
            winner = team1
            winner_score = team1_score
            loser = team2
            loser_score = team2_score
        else:
            winner = team2
            winner_score = team2_score
            loser = team1
            loser_score = team1_score
    final_score = {
        'draw':draw,'winner':winner,'loser':loser,
        'winner_score':winner_score,'loser_score':loser_score,
    }
    return final_score

def update_draw_stats(team1,team2,team1_score,team2_score):
    # update stats on a draw
    Stats.objects.filter(team__in=[team1,team2]).update(GP=F('GP')+1)
    Stats.objects.filter(team__in=[team1,team2]).update(D=F('D')+1)
    Stats.objects.filter(team__in=[team1,team2]).update(streak=0)
    Stats.objects.filter(team__in=[team1,team2]).update(change=0)

def update_stats(winner,loser,final_score):
    # update winner and loser stats
    winner_stats = Stats.objects.filter(team=winner)
    print(winner)
    loser_stats = Stats.objects.filter(team=loser)
    Stats.objects.filter(team__in=[winner,loser]).update(GP=F('GP')+1)

    winner_stats.update(W=F('W')+1)
    loser_stats.update(L=F('L')+1)
    winner_stats.update(streak=1) if winner_stats[0].streak < 0 else winner_stats.update(streak=F('streak')+1)
    loser_stats.update(streak=-1) if loser_stats[0].streak > 0 else loser_stats.update(streak=F('streak')-1)
    winner_stats.update(CF=F('CF')+final_score['winner_score'])
    loser_stats.update(CF=F('CF')+final_score['loser_score'])
    winner_stats.update(CA=F('CA')+final_score['loser_score'])
    loser_stats.update(CA=F('CA')+final_score['winner_score'])
    winner_diff = final_score['winner_score'] - final_score['loser_score']
    loser_diff = -(winner_diff)
    winner_stats.update(CD=F('CD')+ winner_diff)
    loser_stats.update(CD=F('CD')+ loser_diff)
def update_rank_change(winner,loser):
    # if winner was a lower rank, the winner takes the loser's rank and
    # everyone inbetween gets moved down one spot.
    winner_stats = Stats.objects.filter(team=winner)
    loser_stats = Stats.objects.filter(team=loser)
    winner_roster = Roster.objects.filter(team_name=winner)
    loser_roster = Roster.objects.filter(team_name=loser)
    winner_rank = winner_roster[0].rank
    loser_rank = loser_roster[0].rank

    changes = [] # all the rosters in between that need to be moved down
    if winner_rank > loser_rank:
        for i in range((loser_rank+1),winner_rank):
            changes.append(Roster.objects.filter(rank=i).first())
        winner_roster.update(rank=loser_rank)
        loser_roster.update(rank=loser_rank+1)
        Roster.objects.filter(team_name__in=changes).update(rank=F('rank')+1)
        Stats.objects.filter(team__in=changes).update(change=-1)
    winner_stats.update(change=(winner_rank-winner_roster[0].rank))
    loser_stats.update(change=(loser_rank-loser_roster[0].rank))

def finialize_game(g1,g2):
    # update stats if is not draw, otherwise do something different
    final_score = get_final_score(g1,g2)
    if not final_score['draw']:
        winner = final_score['winner']
        loser = team=final_score['loser']
        update_stats(winner,loser,final_score)
        update_rank_change(winner,loser)
    return final_score
def prepare_games(challenge,form):
    # team 1 is always challenger, team 2 always challenged
    prepared_games = {}
    team1 = challenge.challenger.team_name
    team2 = challenge.challenged.team_name
    g1_t1_score = form.cleaned_data['g1_t1_score']
    g1_t2_score = form.cleaned_data['g1_t2_score']
    g2_t1_score = form.cleaned_data['g2_t1_score']
    g2_t2_score = form.cleaned_data['g2_t2_score']
    match_id= generate_match_id()
    prepared_games['g1'] = create_result({'team1':team1,'team2':team2,'team1_score':g1_t1_score,'team2_score':g1_t2_score,'match_id':match_id})
    match_id= generate_match_id()
    prepared_games['g2'] = create_result({'team1':team1,'team2':team2,'team1_score':g2_t1_score,'team2_score':g2_t2_score,'match_id':match_id})
    return prepared_games
def create_result(prepared_game):
    result = Result(
        match_id=prepared_game['match_id'],team1=prepared_game['team1'],team2=prepared_game['team2'],
        team1_score=prepared_game['team1_score'],team2_score=prepared_game['team2_score']
    )
    result.save()
    return result
def generate_match_id():
    allowed_values = list(range(1111111, 10000000))
    current_ids = [result.match_id for result in Result.objects.all()]
    for match_id in current_ids:
        allowed_values.remove(match_id)
    random_value = random.choice(allowed_values)
    return random_value
def update_challenge(challenge_id,g1,g2,final_score):
    challenge = Challenge.objects.filter(pk=challenge_id)
    challenge.update(g1_results=g1)
    challenge.update(g2_results=g2)
    challenge.update(play_date=date.today())
    challenge.update(played=True)
    if final_score['draw']:
        challenge.update(winner=None)
        challenge.update(loser=None)
    else:
        challenge.update(winner=Roster.objects.get(team_name=final_score['winner']))
        challenge.update(loser=Roster.objects.get(team_name=final_score['loser']))
    Stats.objects.filter(team=challenge[0].challenger).update(challengeOut=F('challengeOut')-1)
    Stats.objects.filter(team=challenge[0].challenged).update(challengeIn=F('challengeIn')-1)
