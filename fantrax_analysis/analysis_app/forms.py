from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class UploadForm(forms.Form):
    project_name = forms.FileField()


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']  # list details obtained from reading the docs.


class EightyEightForm(forms.Form):
    agg_or_single = forms.ChoiceField(choices=(('agg', 'agg'), ('single', 'single'),), required=True)
    first_gameweek = forms.IntegerField()
    last_gameweek = forms.IntegerField()
    number_of_team_per_gw = forms.IntegerField()
