from django.db import models
import django_tables2 as tables

class Rosters(models.Model):
    id = models.SmallIntegerField(blank=True, null=False, primary_key=True)
    teams = models.CharField(max_length=100, blank=True, null=True)
    rank = models.SmallIntegerField(blank=True, null=True)
    captain = models.CharField(max_length=100, blank=True, null=True)
    co_captain = models.CharField(max_length=100, blank=True, null=True)
    member1 = models.CharField(max_length=100, blank=True, null=True)
    member2 = models.CharField(max_length=100, blank=True, null=True)
    member3 = models.CharField(max_length=100, blank=True, null=True)
    member4 = models.CharField(max_length=100, blank=True, null=True)
    member5 = models.CharField(max_length=100, blank=True, null=True)
    member6 = models.CharField(max_length=100, blank=True, null=True)
    active = models.CharField(max_length=100, blank=True, null=True)
    server = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rosters'

class RostersTable(tables.Table):
    class Meta:
        model = Rosters
