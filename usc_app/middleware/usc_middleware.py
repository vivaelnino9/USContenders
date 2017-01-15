from django.db.models import F
from django.db.models import Q
from datetime import date

from usc_app.models import *
from notify.signals import notify
from notify.models import Notification

from urllib.request import urlopen
from bs4 import BeautifulSoup


class ResultsMiddleware(object):
    def process_request(self,request):
        if 'admin' not in request.path:
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
                    if team1.get_text() != 'public':
                    # find a private game
                        for challenge in Challenge.objects.filter(played=False):
                        # loop through current challenges
                            challenge_formatted = challenge.format()
                            if [team1.get_text(),team2.get_text()]==challenge_formatted or [team2.get_text(),team1.get_text()]==challenge_formatted:
                            # see if games is what we are looking for
                                match_id = int(row.find_all('td')[0].get_text()[1:])
                                if not Result.objects.filter(match_id=match_id):
                                # if match result hasn't been used already, create result object
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
                                    # if game 1 hasn't been played yet, assign result object as so
                                        c.update(g1_results=result)
                                    else:
                                    # result assigned to game 2
                                        c.update(g2_results=result)
                                        c.update(play_date=date.today())
                                        c.update(played=True)
                                        challenger.update(challengeOut=F('challengeOut')-1)
                                        challenged.update(challengeIn=F('challengeIn')-1)
                                        t1.update(GP=F('GP')+1)
                                        t2.update(GP=F('GP')+1)
                                        t1.update(lastActive=date.today())
                                        t2.update(lastActive=date.today())
                                        score1 = int(score1)
                                        score2 = int(score2)
                                        if challenge.g1_results.team1 == team2:
                                        # this is used to handle whether or not teams switch sides after game 1 or not
                                            t1final = challenge.g1_results.score1 + score2
                                            t2final = challenge.g1_results.score2 + score1
                                        else:
                                            t1final = challenge.g1_results.score1 + score1
                                            t2final = challenge.g1_results.score2 + score2
                                        # from here on teams are labeled as who they were in game 1 (t2 or t2)
                                        t1 = Stats.objects.filter(abv=challenge.g1_results.team1)
                                        t2 = Stats.objects.filter(abv=challenge.g1_results.team2)
                                        if t1final != t2final:
                                        # if there is a winner
                                            if t1final > t2final:
                                            # deteremine who winner and loser is
                                                winner_stats = t1
                                                loser_stats = t2
                                            elif t2final > t1final:
                                                winner_stats = t2
                                                loser_stats = t1

                                            winner_stats.update(W=F('W')+1)
                                            loser_stats.update(L=F('L')+1)

                                            winner_roster = Roster.objects.filter(team_name=winner_stats[0].team)
                                            loser_roster = Roster.objects.filter(team_name=loser_stats[0].team)

                                            wrank = winner_roster[0].rank
                                            lrank = loser_roster[0].rank

                                            changes = []
                                            if wrank > lrank:
                                            # if team that won was a lower rank, handle the shifts in positions
                                            # Logic is:
                                                # - Loser takes winner's rank
                                                # - Everyone in between them, including Loser, drop down by 1
                                                #    (increase rank by 1 - 2nd to 3rd, 3rd to 4th, etc.)
                                                for i in range((lrank+1),wrank):
                                                    changes.append(Roster.objects.filter(rank=i).first())
                                                winner_roster.update(rank=lrank)
                                                loser_roster.update(rank=lrank+1)
                                                Roster.objects.filter(team_name__in=changes).update(rank=F('rank')+1)
                                                Stats.objects.filter(team__in=changes).update(change=-1)
                                            winner_stats.update(change=(wrank-winner_roster[0].rank))
                                            loser_stats.update(change=(lrank-loser_roster[0].rank))
                                            if winner_stats[0].streak < 0:
                                                # used for determining effect game result has on Winner and Loser's streak
                                                winner_stats.update(streak=1)
                                            else:
                                                winner_stats.update(streak=F('streak')+1)
                                            if loser_stats[0].streak > 0:
                                                loser_stats.update(streak=-1)
                                            else:
                                                loser_stats.update(streak=F('streak')-1)

                                            if winner_roster[0].rank > winner_stats[0].highestRank:
                                                # if Winner's rank now is greater than previous highest rank,
                                                # make new rank his highest rank
                                                winner_stats.update(highestRank=winner_roster[0].rank)
                                        else:
                                        # game ended up as a draw
                                            t1.update(D=F('D')+1)
                                            t2.update(D=F('D')+1)
                                            t1.update(streak=0)
                                            t2.update(streak=0)
                                            t1.update(change=0)
                                            t2.update(change=0)
        return None
