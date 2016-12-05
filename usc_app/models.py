from django.db import models
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

class Player(models.Model):
    name = models.CharField(max_length=50)
    minutes = models.PositiveIntegerField(blank=True,null=True)
    tags = models.PositiveIntegerField(blank=True,null=True)
    captures = models.PositiveIntegerField(blank=True,null=True)
    hold = models.CharField(max_length=10,blank=True,null=True)
    returns = models.PositiveIntegerField(blank=True,null=True)

    class Meta:
        db_table = 'player'

    def __str__(self):
        return self.name


class Roster(models.Model):
    team_name = models.CharField(max_length=50)
    abv = models.CharField(max_length=3)
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
        db_table = 'roster'
    def __str__(self):
        return self.team_name

    def save(self, *args, **kwargs):
        stats = Stats(team=self.team_name)
        stats.save()
        super(Roster, self).save(*args, **kwargs)

    def getChallengers(self):
        challengers = {}
        rosters = Roster.objects.all().order_by('rank')
        for roster in rosters:
            # Create list of challengers (teams 4 spots above current team)
            if self.rank - roster.rank <= 4 and self.rank - roster.rank > 0:
                challengers[roster.rank]= Stats.objects.filter(team=roster.team_name)
        # sorted_challengers = sorted(challengers.items(), key=operator.itemgetter(0))
        return challengers

class Stats(models.Model):
     change = models.IntegerField(
        null=True,
        blank=True,
        default=0
    )
     team = models.CharField(max_length=50)
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
        null=True,
        blank=True,
        default=0
    )
     class Meta:
         db_table = 'stats'

class Challenge(models.Model):
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
    map = models.CharField(max_length=50)
    challenge_date = models.DateTimeField(default=datetime.now())
    forfeit_date = models.DateTimeField(default=datetime.now()+timedelta(days=5))
    void_date = models.DateTimeField(default=datetime.now()+timedelta(days=14))
    play_date = models.DateTimeField(blank=True,null=True)

class Captain(Player):
    user = models.OneToOneField(User)
    team = models.ForeignKey(
        Roster,
        related_name='team',
        verbose_name='Team',
        blank=True,null=True
    )
    class Meta:
        db_table = 'captain'

    def __str__(self):
        return self.user.username
