from django.db import models
import datetime
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.shortcuts import get_object_or_404
from django.db.models import F
from .choices import *

class User(AbstractUser):
    team = models.CharField(
        max_length=50,
        default='',
        blank=True,null=True
    )
    class Meta:
        db_table = 'users'

class Player(models.Model):
    user = models.OneToOneField(User)
    name = models.CharField(max_length=50)
    minutes = models.PositiveIntegerField(blank=True,null=True,default=0)
    tags = models.PositiveIntegerField(blank=True,null=True,default=0)
    captures = models.PositiveIntegerField(blank=True,null=True,default=0)
    hold = models.CharField(max_length=10,blank=True,null=True,default=0)
    returns = models.PositiveIntegerField(blank=True,null=True,default=0)
    class Meta:
        db_table = 'players'

    def __str__(self):
        return self.name

class FreeAgent(models.Model):
    user = models.OneToOneField(User,verbose_name='User')
    name = models.CharField(max_length=50,verbose_name='Name')
    eligible = models.BooleanField(verbose_name='Eligible?',default=True)
    server = models.IntegerField(
        choices=SERVER_CHOICES,
        verbose_name='Server',
    )
    position = models.IntegerField(
        choices=POSITION_CHOICES,
        verbose_name='Position'
    )
    mic = models.BooleanField(default=True,verbose_name='Mic?')
    tagpro_profile = models.URLField(
        max_length=200,
        verbose_name="TagPro Profile",
        blank=True,null=True
    )
    reddit_info = models.URLField(
        max_length=200,
        verbose_name="Reddit Info",
        blank=True,null=True
    )
    tagpro_stats = models.URLField(
        max_length=200,
        verbose_name="TagPro Stats",
        blank=True,null=True
    )
    additional_notes = models.TextField(max_length=500,blank=True,null=True)
    class Meta:
        db_table = 'free_agents'

    def __str__(self):
        return self.name

class Roster(models.Model):
    # eligible = models.BooleanField(default=False)
    team_name = models.CharField(max_length=50)
    abv = models.CharField(max_length=4)
    rank = models.PositiveIntegerField()
    captain = models.ForeignKey(
        'usc_app.Captain',
        on_delete=models.CASCADE,
        related_name='captain',
        verbose_name='Captain',
        blank=True,null=True
    )
    co_captain = models.ForeignKey(
        Player,
        on_delete=models.SET_NULL,
        related_name='co_captain',
        verbose_name='Co-Captain',
        blank=True,null=True
    )
    member1 = models.ForeignKey(
        Player,
        on_delete=models.SET_NULL,
        related_name='member1',
        verbose_name='Member1',
        blank=True,null=True
    )
    member2 = models.ForeignKey(
        Player,
        on_delete=models.SET_NULL,
        related_name='member2',
        verbose_name='Member2',
        blank=True,null=True
    )
    member3 = models.ForeignKey(
        Player,
        on_delete=models.SET_NULL,
        related_name='member3',
        verbose_name='Member3',
        blank=True,null=True
    )
    member4 = models.ForeignKey(
        Player,
        on_delete=models.SET_NULL,
        related_name='member4',
        verbose_name='Member4',
        blank=True,null=True
    )
    member5 = models.ForeignKey(
        Player,
        on_delete=models.SET_NULL,
        related_name='member5',
        verbose_name='Member5',
        blank=True,null=True
    )
    member6 = models.ForeignKey(
        Player,
        on_delete=models.SET_NULL,
        related_name='member6',
        verbose_name='Member6',
        blank=True,null=True
    )
    firstActive = models.DateField(blank=True,null=True)
    daysActive = models.PositiveIntegerField()
    server = models.IntegerField(
        choices=SERVER_CHOICES,
        verbose_name='Server',
    )
    logo = models.ImageField(
        'logo',
        max_length=100,
        upload_to='photos',
        blank=True
    )

    class Meta:
        db_table = 'rosters'
    def __str__(self):
        return self.team_name

    def getChallengers(self):
        challengers = {}
        rosters = Roster.objects.all().order_by('rank')
        for roster in rosters:
            # Create list of challengers (teams 4 spots above current team)
            if self.rank - roster.rank <= 4 and self.rank - roster.rank > 0:
                roster_stats = Stats.objects.get(team=roster.team_name)
                if roster_stats.get_challengeIn() < 2:
                    challengers[roster.rank] = roster_stats
        return challengers

class Stats(models.Model):
    change = models.IntegerField(
        null=True,
        blank=True,
        default=0
    )
    team = models.CharField(max_length=50)
    abv = models.CharField(max_length=4)
    streak = models.IntegerField(
        null=True,
        blank=True,
        default=0
    )
    highestRank = models.PositiveIntegerField(
        null=True,
        blank=True,
        default=0
    )
    uscmRank = models.PositiveIntegerField(
        null=True,
        blank=True,
        default=0
    )
    lastActive = models.DateField(blank=True,null=True)
    GP = models.PositiveIntegerField(
        null=True,
        blank=True,
        default=0
    )
    W = models.IntegerField(
        null=True,
        blank=True,
        default=0
    )
    L = models.IntegerField(
        null=True,
        blank=True,
        default=0
    )
    D = models.IntegerField(
        null=True,
        blank=True,
        default=0
    )
    F = models.IntegerField(
        null=True,
        blank=True,
        default=0
    )
    CF = models.IntegerField(
        null=True,
        blank=True,
        default=0
    )
    CA = models.IntegerField(
        null=True,
        blank=True,
        default=0
    )
    CD = models.IntegerField(
        null=True,
        blank=True,
        default=0
    )
    CDperG = models.FloatField(
        verbose_name='CD/G',
        null=True,
        blank=True,
        default=0
    )
    rankPoints = models.PositiveIntegerField(
        null=True,
        blank=True,
        default=0
    )
    class Meta:
        db_table = 'stats'

    def __str__(self):
        return self.team

    def get_cdperg(self):
        if self.GP == 0:
            return 0
        else:
            return self.CD/self.GP

    def get_challengeIn(self):
        self_roster = Roster.objects.get(pk=self.id)
        return Challenge.objects.filter(challenged=self_roster).filter(played=False).count()

    def get_challengeOut(self):
        self_roster = Roster.objects.get(pk=self.id)
        return Challenge.objects.filter(challenger=self_roster).filter(played=False).count()

class Challenge(models.Model):
    played = models.BooleanField(default=False,verbose_name='Played?')
    challenger = models.ForeignKey(
        Roster,
        related_name='challenger',
        verbose_name='Challenger',
    )
    challenged = models.ForeignKey(
        Roster,
        related_name='challenged',
        verbose_name='Challenged',
    )
    map = models.CharField(max_length=50,verbose_name='Map')
    challenge_date = models.DateField(default=datetime.date.today,verbose_name='Challenge Date')
    forfeit_date = models.DateField(default=datetime.date.today()+timedelta(days=5), verbose_name='Forfeit Date')
    void_date = models.DateField(default=datetime.date.today()+timedelta(days=14), verbose_name='Void Date')
    play_date = models.DateField(blank=True,null=True, verbose_name='Date Played')
    g1_results = models.ForeignKey(
        'usc_app.Result',
        related_name='g1_results',
        verbose_name='Game 1 Results',
        null=True,blank=True,
    )
    g2_results = models.ForeignKey(
        'usc_app.Result',
        related_name='g2_results',
        verbose_name='Game 2 Results',
        null=True,blank=True,
    )
    g1_submitted = models.ForeignKey(
        'usc_app.Result',
        related_name='g1_submitted',
        verbose_name='Game 1 Submitted',
        null=True,blank=True,
    )
    g2_submitted = models.ForeignKey(
        'usc_app.Result',
        related_name='g2_submitted',
        verbose_name='Game 2 Submitted',
        null=True,blank=True,
    )
    submitted_by = models.ForeignKey(
        User,
        related_name='submitted_by',
        verbose_name='Submitted By',
        null=True,blank=True,
    )
    winner = models.ForeignKey(
        Roster,
        related_name='winner',
        verbose_name='Winner',
        null=True,blank=True,
    )
    loser = models.ForeignKey(
        Roster,
        related_name='loser',
        verbose_name='Loser',
        null=True,blank=True,
    )
    approved = models.BooleanField(default=False,verbose_name='Approved?')
    class Meta:
        db_table = 'challenges'

    def __str__(self):
        return self.challenger.team_name + ' vs. ' + self.challenged.team_name

    def format(self):
        match = [self.challenger.abv,self.challenged.abv]
        return match

class Result(models.Model):
    match_id = models.PositiveIntegerField(
        verbose_name='Match ID',
        blank=True,null=True
    )
    team1 = models.CharField(
        max_length=50,
        verbose_name='Team 1',
        blank=True,null=True
    )
    team2 = models.CharField(
        max_length=50,
        verbose_name='Team 2',
        blank=True,null=True
    )
    team1_score = models.PositiveIntegerField(
        default=0,
        verbose_name='Score 1',
        blank=True,null=True
    )
    team2_score = models.PositiveIntegerField(
        default=0,
        verbose_name='Score 2',
        blank=True,null=True
    )

    class Meta:
        db_table = 'results'

    def __str__(self):
        return str(self.match_id)

    def show_server(self):
        return self.server.lower()


class Captain(Player):
    team = models.ForeignKey(
        Roster,
        related_name='team',
        verbose_name='Team',
        blank=True,null=True
    )
    class Meta:
        db_table = 'captains'

    def __str__(self):
        return self.user.username
