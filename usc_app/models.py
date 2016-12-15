from django.db import models
import datetime
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import F

class Player(models.Model):
    name = models.CharField(max_length=50)
    minutes = models.PositiveIntegerField(blank=True,null=True)
    tags = models.PositiveIntegerField(blank=True,null=True)
    captures = models.PositiveIntegerField(blank=True,null=True)
    hold = models.CharField(max_length=10,blank=True,null=True)
    returns = models.PositiveIntegerField(blank=True,null=True)

    class Meta:
        db_table = 'players'

    def __str__(self):
        return self.name


class Roster(models.Model):
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
        on_delete=models.CASCADE,
        related_name='co_captain',
        verbose_name='Co-Captain',
        blank=True,null=True
    )
    member1 = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='member1',
        verbose_name='Member1',
        blank=True,null=True
    )
    member2 = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='member2',
        verbose_name='Member2',
        blank=True,null=True
    )
    member3 = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='member3',
        verbose_name='Member3',
        blank=True,null=True
    )
    member4 = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='member4',
        verbose_name='Member4',
        blank=True,null=True
    )
    member5 = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='member5',
        verbose_name='Member5',
        blank=True,null=True
    )
    member6 = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='member6',
        verbose_name='Member6',
        blank=True,null=True
    )
    firstActive = models.CharField(max_length=50)
    daysActive = models.PositiveIntegerField()
    server = models.CharField(max_length=50)
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

    def save(self, *args, **kwargs):
        stats = Stats(team=self.team_name,abv=self.abv)
        stats.save()
        super(Roster, self).save(*args, **kwargs)

    def getChallengers(self):
        challengers = {}
        rosters = Roster.objects.all().order_by('rank')
        for roster in rosters:
            # Create list of challengers (teams 4 spots above current team)
            if self.rank - roster.rank <= 4 and self.rank - roster.rank > 0:
                challengers[roster.rank]= Stats.objects.filter(team=roster.team_name).first()
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
    lastActive = models.CharField(max_length=50,blank=True)
    challengeOut = models.PositiveIntegerField(
        null=True,
        blank=True,
        default=0
    )
    challengeIn = models.PositiveIntegerField(
        null=True,
        blank=True,
        default=0
    )
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
    CDperG = models.IntegerField(
        verbose_name='CD/G',
        null=True,
        blank=True,
        default=0
    )
    class Meta:
        db_table = 'stats'

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
    g1_results = models.OneToOneField(
        'usc_app.Result',
        related_name='g1_results',
        verbose_name='Game 1 Results',
        null=True,blank=True,
    )
    g2_results = models.OneToOneField(
        'usc_app.Result',
        related_name='g2_results',
        verbose_name='Game 2 Results',
        null=True,blank=True,
    )
    class Meta:
        db_table = 'challenges'

    def format(self):
        match = [self.challenger.abv,self.challenged.abv]
        return match

class Result(models.Model):
    match_id = models.CharField(
        max_length=50,
        verbose_name='Match ID',
        blank=True,null=True
    )
    server = models.CharField(
        max_length=50,
        verbose_name='Server',
        blank=True,null=True
    )
    duration = models.CharField(
        max_length=50,
        verbose_name='Duration',
        blank=True,null=True
    )
    finished = models.BooleanField(
        default=True,
        verbose_name="Finished",
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
    score1 = models.PositiveIntegerField(
        default=0,
        verbose_name='Score 1',
        blank=True,null=True
    )
    score2 = models.PositiveIntegerField(
        default=0,
        verbose_name='Score 2',
        blank=True,null=True
    )

    class Meta:
        db_table = 'results'

    def __str__(self):
        return self.match_id

    def save(self, *args, **kwargs):
        team1 = Stats.objects.filter(abv=self.team1)
        team2 = Stats.objects.filter(abv=self.team2)

        team1.update(CF=F('CF')+self.score1)
        team1.update(CA=F('CA')+self.score2)

        team2.update(CF=F('CF')+self.score2)
        team2.update(CA=F('CA')+self.score1)

        super(Result, self).save(*args, **kwargs)

    def show_server(self):
        return self.server.lower()

class Captain(Player):
    user = models.OneToOneField(User)
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
