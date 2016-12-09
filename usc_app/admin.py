from django.contrib import admin
from django import forms
from .models import *


class PlayerAdminForm(forms.ModelForm):
    model = Player

class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'minutes','tags','captures','hold','returns')
    list_filter = ['name',]
    search_fields = ['name',]
    list_per_page = 10
    form = PlayerAdminForm

admin.site.register(Player,PlayerAdmin)

class TeamRosterAdminForm(forms.ModelForm):
    model = Roster

class TeamRosterAdmin(admin.ModelAdmin):
    fields = ['team_name','abv','rank','captain','co_captain','member1','member2','member3','member4','member5','member6','firstActive','daysActive','server','logo']
    list_display = (
        'team_name', 'rank',
    )
    list_filter = ['team_name',]
    search_fields = ['team_name',]
    list_per_page = 10
    form = TeamRosterAdminForm

admin.site.register(Roster,TeamRosterAdmin)
class TeamStatsAdminForm(forms.ModelForm):
    model = Stats

class TeamStatsAdmin(admin.ModelAdmin):
    fields = ['change','team','abv','streak','highestRank','uscmRank','lastActive','challengeOut','challengeIn','GP','W','L','D','F','CF','CA','CD','CDperG']
    list_display = ['team']
    list_filter = ['team',]
    search_fields = ['team',]
    list_per_page = 10
    form = TeamRosterAdminForm
admin.site.register(Stats,TeamStatsAdmin)

class ChallengeAdminForm(forms.ModelForm):
    model = Challenge

class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('played','challenger', 'challenged','map','challenge_date','forfeit_date','void_date','play_date','g1_results','g2_results')
    list_filter = ['played','challenger','challenged']
    search_fields = ['played','challenger','challenged']
    list_per_page = 10
    form = ChallengeAdminForm

admin.site.register(Challenge,ChallengeAdmin)

class ResultAdminForm(forms.ModelForm):
    model = Result

class ResultAdmin(admin.ModelAdmin):
    list_display = ('match_id','server','duration','finished','team1','team2','score1','score2')
    list_filter = ['match_id','team1','team2']
    search_fields = ['match_id','team1','team2']
    list_per_page = 10
    form = ResultAdminForm

admin.site.register(Result,ResultAdmin)

admin.site.register(Captain)
