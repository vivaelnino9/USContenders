import string
import random
from django import forms
from .models import *
from django.core.validators import ValidationError
from django.core.exceptions import ObjectDoesNotExist
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
        challenger = Roster.objects.filter(team_name=request.user.team).first()
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
    team_name = forms.CharField(label='Team Name',max_length=50)
    server = forms.ChoiceField(choices=SERVER_CHOICES, label="Server", initial='', widget=forms.Select(), required=True)
    captain = forms.CharField(label='Captain',max_length=50)
    co_captain = forms.CharField(label='Co-Captain',max_length=50)
    member1 = forms.CharField(label='Member',max_length=50)
    member2 = forms.CharField(label='Member',max_length=50)
    member3 = forms.CharField(label='Member',max_length=50,required=False)
    member4 = forms.CharField(label='Member',max_length=50,required=False)
    member5 = forms.CharField(label='Member',max_length=50,required=False)
    member6 = forms.CharField(label='Member',max_length=50,required=False)
    class Meta:
        model = Roster
        fields = (
            'captain','team_name','server','co_captain','member1',
            'member2','member3','member4','member5',
        )
    def clean(self):
        cleaned_data = super(RosterForm, self).clean()
        team = self.cleaned_data['team_name']
        server = self.cleaned_data['server']
        captain = self.cleaned_data['captain']
        co_captain = self.cleaned_data['co_captain']
        member1 = self.cleaned_data['member1']
        member2 = self.cleaned_data['member2']
        avoid = ['team_name','server']
        player_list = {
            'captain':captain,'co_captain':co_captain,
            'member1':member1,'member2':member2,
        }
        for field,value in cleaned_data.items():
            if field not in avoid:
                if value != '':
                    player_list[field] = value
                else:
                    self.cleaned_data[field] = None

        rosterExists = Roster.objects.filter(team_name=team).exists()

        if rosterExists:
            self.clear_data(cleaned_data,avoid)
            msg = 'That team name is already being used by another team!'
            self.add_error('team_name', msg)
            return cleaned_data

        for label,player in player_list.items():
            try:
                u = User.objects.get(username=player)
                if u.team != '':
                    self.clear_data(cleaned_data,avoid)
                    msg = player+' is already on a team!'
                    self.add_error(label, msg)
                    return cleaned_data
            except ObjectDoesNotExist:
                pass
        self.make_players(player_list,team,captain)
        return cleaned_data

    def clear_data(self,cleaned_data,avoid):
        for field in cleaned_data:
            if field not in avoid:
                self.cleaned_data[field] = None

    def make_players(self,player_list,team,captain):
        for label,player in player_list.items():
            try:
                user = User.objects.get(username=player)
                User.objects.filter(username=user.username).update(team=team)
                if label == 'captain':
                    try:
                        captain = Captain.objects.get(name=player,user=user)
                    except ObjectDoesNotExist:
                        captain = Captain.objects.create(name=player,user=user)
                    self.cleaned_data['captain'] = captain
                else:
                    try:
                        p = Player.objects.get(name=player,user=user)
                    except ObjectDoesNotExist:
                        p = Player.objects.create(name=player,user=user)
                    self.cleaned_data[label] = p
            except ObjectDoesNotExist:
                password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
                user = User.objects.create(username=player,password=password,team=team)
                if label == 'captain':
                    self.cleaned_data['captain'] = Captain.objects.create(name=captain,user=user)
                else:
                    self.cleaned_data[label] = Player.objects.create(name=player,user=user)

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
    tagpro_profile = forms.URLField(
        label='Tagpro Profile',
        max_length=200,
    )
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
            user = User.objects.get(username=name)
            if user.team != '':
                msg = name+' is already on a team!'
                self.add_error('name', msg)
        return cleaned_data
class AddPlayerForm(forms.ModelForm):
    name = forms.CharField(label='Name',max_length=50)
    class Meta:
        model = Player
        fields = (
            'name',
        )

    def clean(self):
        cleaned_data = super(AddPlayerForm, self).clean()
        name = cleaned_data.get('name')
        if User.objects.filter(username=name).exists():
            user = User.objects.get(username=name)
            if user.team != '':
                msg = name+' is already on a team!'
                self.add_error('name', msg)
            else:
                self.user = user
        else:
            user = User.objects.create(username=name)
            self.user = user
