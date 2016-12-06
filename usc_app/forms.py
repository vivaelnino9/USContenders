from django import forms
from .models import *
from django.core.validators import ValidationError
from django.utils.translation import gettext as _

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
            existingChallenge = Challenge.objects.filter(challenger=challenger.id).filter(challenged=challenged[0].id)
            if challenged[0].challengeIn < 2 and not existingChallenge:
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
        fields = ('username','email','password')

class CaptainForm(forms.ModelForm):
    team = forms.ModelChoiceField(queryset=Roster.objects.filter(captain__isnull=True), required=True)
    class Meta:
        model = Captain
        fields = ('team',)
