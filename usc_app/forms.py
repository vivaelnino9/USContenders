from django import forms
from .models import *
from django.core.validators import ValidationError
from django.utils.translation import gettext as _
from datetime import date
from django.db.models import Q
from .choices import *

class ChallengeForm(forms.ModelForm):
    challenged = forms.ModelChoiceField(queryset=Roster.objects.all(), required=True, help_text="Choose who to challenge!")
    map = forms.CharField(label='Map', max_length=50)

    class Meta:
        model = Challenge
        fields = ('challenged', 'map')

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super(ChallengeForm, self).__init__(*args, **kwargs)
        challenger = Roster.objects.filter(team_name=request.user.first_name).first()
        canChallenge = challenger.getChallengers()
        ranks = []
        for rank,challenged in canChallenge.items():
            existingChallenge = Challenge.objects.filter(Q(challenger=challenger.id)|Q(challenged=challenged.id)).filter(played=False)
            if challenged.challengeIn < 2 and not existingChallenge:
                ranks.append(rank)
        self.fields['challenged'] = forms.ModelChoiceField(queryset=Roster.objects.exclude(team_name=challenger.team_name).filter(rank__in=ranks), required=True, help_text="Choose who to challenge!")
    def clean_challenged(self):
        challenged = self.cleaned_data['challenged']
        challengeIn = Stats.objects.filter(team=challenged.team_name).first().challengeIn
        if (challengeIn + 1) > 2:
            raise ValidationError(
                        _('%(team)s already has 2 challenges in! '),
                        params={'team':challenged.team_name },
                    )
        return challenged

class ChallengeArgForm(forms.ModelForm):
    map = forms.CharField(label='Map', max_length=50)

    class Meta:
        model = Challenge
        fields = ('map',)
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username','password')

class RosterForm(forms.ModelForm):
    team = forms.CharField(label='Team Name',max_length=50)
    abv = forms.CharField(label='Team Abbreviation',max_length=4)
    server = forms.CharField(label='Server',max_length=50,)
    co_captain = forms.CharField(label='Co-Captain',max_length=50)
    member1 = forms.CharField(label='Member',max_length=50)
    member2 = forms.CharField(label='Member',max_length=50)
    member3 = forms.CharField(label='Member',max_length=50,required=False)
    member4 = forms.CharField(label='Member',max_length=50,required=False)
    member5 = forms.CharField(label='Member',max_length=50,required=False)
    member6 = forms.CharField(label='Member',max_length=50,required=False)
    class Meta:
        model = Captain
        fields = (
            'team','abv','server','co_captain','member1',
            'member2','member3','member4','member5',
        )

    def clean(self):
        cleaned_data = super(RosterForm, self).clean()
        team = self.cleaned_data['team']
        abv = self.cleaned_data['abv']
        server = self.cleaned_data['server']
        co_captain = self.cleaned_data['co_captain']
        member1 = self.cleaned_data['member1']
        member2 = self.cleaned_data['member2']
        member3 = self.cleaned_data['member3']
        player_list = [
            co_captain,member1,member2
        ]
        if self.cleaned_data['member3']:
            member3 = self.cleaned_data['member3']
            player_list.append(member3)
        if self.cleaned_data['member4']:
            member4 = self.cleaned_data['member4']
            player_list.append(member4)
        if self.cleaned_data['member5']:
            member5 = self.cleaned_data['member5']
            player_list.append(member5)
        if self.cleaned_data['member6']:
            member6 = self.cleaned_data['member6']
            player_list.append(member6)
        rosterExists = Roster.objects.filter(team_name=team).exists()
        abvExists =  Roster.objects.filter(abv=abv).exists()
        playerExists = Player.objects.filter(name__in=player_list).exists()

        if rosterExists or abvExists or playerExists:
            if rosterExists:
                msg = 'That team name is already being used by another team!'
                self.add_error('team', msg)
            elif abvExists:
                msg = 'That abbreviation is already being used by another team!'
                self.add_error('team', msg)
            else:
                for player in player_list:
                    if Player.objects.filter(name=player).exists():
                        msg = player+' is already on a team!'
                        self.add_error('team', msg)
        else:
            if Roster.objects.count() > 0:
                rank = (Roster.objects.all().order_by('-rank')[0].rank)+1
            else:
                rank = 1
            new_team = Roster(
                team_name=team,
                abv=abv,
                rank=rank,
                co_captain=Player.objects.create(name=co_captain),
                member1=Player.objects.create(name=member1),
                member2=Player.objects.create(name=member2),
                firstActive=date.today(),
                daysActive=0,
                server=server,
            )
            if self.cleaned_data['member3']:
                new_team.member3=Player.objects.create(name=member3)
            if self.cleaned_data['member4']:
                if not self.cleaned_data['member3']:
                    new_team.member3=Player.objects.create(name=member4)
                else:
                    new_team.member4=Player.objects.create(name=member4)
            if self.cleaned_data['member5']:
                if not self.cleaned_data['member3']:
                    new_team.member3=Player.objects.create(name=member5)
                elif not self.cleaned_data['member4']:
                    new_team.member4=Pslayer.objects.create(name=member5)
                else:
                    new_team.member5=Player.objects.create(name=member5)
            if self.cleaned_data['member6']:
                if not self.cleaned_data['member3']:
                    new_team.member3=Player.objects.create(name=member6)
                elif not self.cleaned_data['member4']:
                    new_team.member4=Player.objects.create(name=member6)
                elif not self.cleaned_data['member5']:
                    new_team.member5=Player.objects.create(name=member6)
                else:
                    new_team.member6=Player.objects.create(name=member6)
            for player in player_list:
                User.objects.create(username=player,first_name=team)
            new_team.save()
            self.cleaned_data['team'] = new_team
        return cleaned_data

class ScoresForm(forms.Form):
    g1_t1_score = forms.IntegerField()
    g1_t2_score = forms.IntegerField()
    g2_t1_score = forms.IntegerField()
    g2_t2_score = forms.IntegerField()

    def clean(self):
        cleaned_data = super(ScoresForm, self).clean()
        g1_t1_score = cleaned_data.get('g1_t1_score')
        g1_t2_score = cleaned_data.get('g1_t2_score')
        g2_t1_score = cleaned_data.get('g2_t1_score')
        g2_t2_score = cleaned_data.get('g2_t2_score')

        return cleaned_data

class FAForm(forms.ModelForm):
    name = forms.CharField(label='Name',max_length=50)
    server = forms.ChoiceField(choices=SERVER_CHOICES, label="Server", initial='', widget=forms.Select(), required=True)
    position = forms.ChoiceField(choices=POSITION_CHOICES, label="Position",widget=forms.Select(), required=True)
    mic = forms.BooleanField(label='Mic?',required=False)
    tagpro_profile = forms.URLField(label='Tagpro Profile',max_length=200)
    reddit_info = forms.URLField(
        max_length=200,
        label="Reddit Info",
        required=False
    )
    tagpro_stats = forms.URLField(
        max_length=200,
        label="TagPro Stats Profile",
        required=False
    )
    additional_notes = forms.CharField(max_length=500,required=False)

    class Meta:
        model = FreeAgent
        fields = (
            'name','server','position','mic','tagpro_profile',
            'reddit_info','tagpro_stats','additional_notes',
        )

    def clean(self):
        cleaned_data = super(FAForm, self).clean()
        name = cleaned_data.get('name')
        tagpro_profile = cleaned_data.get('tagpro_profile')
        found = False
        for choice in SERVER_CHOICES:
            server = choice[1].lower()
            url= 'http://tagpro-'+server+'.koalabeast.com/profile/'
            if url in tagpro_profile:
                found = True
        if not found:
            msg = 'Please link your tagpro profile! (i.e. http://tagpro-radius.koalabeast.com/profile/52ca4d0cd00099041a0002e9)'
            self.add_error('tagpro_profile',msg)
        if User.objects.filter(username=name).exists():
            msg = name+' is already on a team!'
            self.add_error('name', msg)
        return cleaned_data
