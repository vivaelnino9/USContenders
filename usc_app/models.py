from django.db import models


class Roster(models.Model):
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
    active = models.CharField(max_length=50)
    server = models.CharField(max_length=50)
    class Meta:
        db_table = 'roster'
