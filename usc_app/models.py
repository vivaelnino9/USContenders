from django.db import models


class TeamRoster(models.Model):
    team = models.CharField(max_length=50)
    rank = models.PositiveIntegerField()
    captain = models.CharField(max_length=50)
    co_captain = models.CharField(max_length=50)
    member1 = models.CharField(max_length=50)
    member2 = models.CharField(max_length=50)
    member3 = models.CharField(max_length=50)
    member4 = models.CharField(max_length=50)
    member5 = models.CharField(max_length=50)
    member6 = models.CharField(max_length=50)
    firstActive = models.CharField(max_length=50)
    daysActive = models.PositiveIntegerField()
    server = models.CharField(max_length=50)
    logo = models.ImageField(
        'logo',
        max_length=100,
        upload_to='photos'
    )
    class Meta:
        db_table = 'roster'

class TeamStats(models.Model):
     change = models.IntegerField(null=True)
     team = models.CharField(max_length=50)
     streak = models.IntegerField(null=True)
     highestRank = models.PositiveIntegerField(null=True)
     uscmRank = models.PositiveIntegerField(null=True)
     lastActive = models.CharField(max_length=50)
     challengeOut = models.PositiveIntegerField(null=True)
     challengeIn = models.PositiveIntegerField(null=True)
     GP = models.PositiveIntegerField(null=True)
     W = models.IntegerField(null=True)
     L = models.IntegerField(null=True)
     D = models.IntegerField(null=True)
     F = models.IntegerField(null=True)
     CF = models.IntegerField(null=True)
     CA = models.IntegerField(null=True)
     CD = models.IntegerField(null=True)
     CDperG = models.IntegerField(null=True)
     class Meta:
         db_table = 'stats'
