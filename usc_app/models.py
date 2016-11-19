from django.db import models


class TeamRoster(models.Model):
    team = models.CharField(max_length=50)
    rank = models.PositiveIntegerField()
    captain = models.CharField(max_length=50)
    co_captain = models.CharField(max_length=50)
    member1 = models.CharField(max_length=50)
    member2 = models.CharField(max_length=50)
    member3 = models.CharField(max_length=50,blank=True)
    member4 = models.CharField(max_length=50,blank=True)
    member5 = models.CharField(max_length=50,blank=True)
    member6 = models.CharField(max_length=50,blank=True)
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

class TeamStats(models.Model):
     change = models.IntegerField(null=True,blank=True)
     team = models.CharField(max_length=50)
     streak = models.IntegerField(null=True,blank=True)
     highestRank = models.PositiveIntegerField(null=True,blank=True)
     uscmRank = models.PositiveIntegerField(null=True,blank=True)
     lastActive = models.CharField(max_length=50,blank=True)
     challengeOut = models.PositiveIntegerField(null=True,blank=True)
     challengeIn = models.PositiveIntegerField(null=True,blank=True)
     GP = models.PositiveIntegerField(null=True,blank=True)
     W = models.IntegerField(null=True,blank=True)
     L = models.IntegerField(null=True,blank=True)
     D = models.IntegerField(null=True,blank=True)
     F = models.IntegerField(null=True,blank=True)
     CF = models.IntegerField(null=True,blank=True)
     CA = models.IntegerField(null=True,blank=True)
     CD = models.IntegerField(null=True,blank=True)
     CDperG = models.IntegerField(null=True,blank=True)
     class Meta:
         db_table = 'stats'
