from django.db.models import F
from django.db.models import Q
from datetime import date

from usc_app.models import *
from usc_app.score_handler import *
from notify.signals import notify
from notify.models import Notification

from urllib.request import urlopen
from bs4 import BeautifulSoup


class ResultsMiddleware(object):
    def process_request(self,request):
        on = True
        if 'admin' not in request.path and on:
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
                            challenge_stats = Challenge.objects.filter(id=challenge.id)
                            if [team1.get_text(),team2.get_text()]==challenge_formatted or [team2.get_text(),team1.get_text()]==challenge_formatted:
                            # see if games is what we are looking for
                                match_id = int(row.find_all('td')[0].get_text()[1:])
                                if not Result.objects.filter(match_id=match_id):
                                # if match result hasn't been used already, create result object
                                    team1 = team1.get_text()
                                    team2 = team2.get_text()
                                    ####
                                    team1_score = row.find_all('td')[9].get_text()
                                    team2_score = row.find_all('td')[10].get_text()
                                    ####
                                    team1_stats = Stats.objects.filter(abv=str(team1))
                                    team2_stats = Stats.objects.filter(abv=str(team2))
                                    ####
                                    team1_roster = Roster.objects.filter(abv=str(team1))
                                    team2_roster = Roster.objects.filter(abv=str(team2))
                                    ####
                                    challenger = Stats.objects.filter(abv=challenge.challenger.abv)
                                    challenged = Stats.objects.filter(abv=challenge.challenged.abv)

                                    result = {'team1':team1_stats[0].team,'team2':team2_stats[0].team,'team1_score':int(team1_score),'team2_score':int(team2_score),'match_id':match_id}

                                    if not challenge.g1_results:
                                        # if game 1 hasn't been played yet, assign result object as so
                                        g1 = create_result(result)
                                        challenge_stats.update(g1_results=g1)
                                    else:
                                        g1 = challenge.g1_results
                                        g2 = create_result(result)
                                        final_score = finialize_game(g1,g2)
                                        update_challenge(challenge.id,g1,g2,final_score)
