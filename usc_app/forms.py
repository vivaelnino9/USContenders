from django import forms

from .models import Challenge, Roster

class ChallengeForm(forms.ModelForm):
    challenger = forms.ModelChoiceField(queryset=Roster.objects.all(), required=True, help_text="You are the challenger.")
    challenged = forms.ModelChoiceField(queryset=Roster.objects.all(), required=True, help_text="Choose who to challenge!")
    map = forms.CharField(label='Map', max_length=50)

    class Meta:
        model = Challenge
        fields = ('challenger', 'challenged', 'map')
