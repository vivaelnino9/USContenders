from django.db import models


class Player(models.Model):
    name = models.CharField(max_length=50)
    roster = models.ForeignKey(
        "usc_app.Roster",
        related_name='roster',
        verbose_name='Team',
        blank=True,null=True
    )
    minutes = models.PositiveIntegerField(blank=True,null=True)
    tags = models.PositiveIntegerField(blank=True,null=True)
    captures = models.PositiveIntegerField(blank=True,null=True)
    hold = models.CharField(max_length=10,blank=True,null=True)
    returns = models.PositiveIntegerField(blank=True,null=True)

    def __str__(self):
        return self.name


class Roster(models.Model):
    team = models.CharField(max_length=50)
    rank = models.PositiveIntegerField()
    captain = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='captain',
        verbose_name='Captain',
    )
    co_captain = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='co_captain',
        verbose_name='Co-Captain',
    )
    member1 = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='member1',
        verbose_name='Member1',
    )
    member2 = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='member2',
        verbose_name='Member2',
    )
    member3 = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='member3',
        verbose_name='Member3',
        blank=True,
        null=True
    )
    member4 = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='member4',
        verbose_name='Member4',
        blank=True,
        null=True
    )
    member5 = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='member5',
        verbose_name='Member5',
        blank=True,
        null=True
    )
    member6 = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='member6',
        verbose_name='Member6',
        blank=True,
        null=True
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

class Stats(models.Model):
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
