from django import forms
from .models import *

class ChallengeForm(forms.ModelForm):
    challenger = forms.ModelChoiceField(queryset=Roster.objects.all(), required=True, help_text="You are the challenger.")
    challenged = forms.ModelChoiceField(queryset=Roster.objects.all(), required=True, help_text="Choose who to challenge!")
    map = forms.CharField(label='Map', max_length=50)

    class Meta:
        model = Challenge
        fields = ('challenger', 'challenged', 'map')

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
