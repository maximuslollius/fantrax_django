from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.forms import UserCreationForm
import os
from django.core.files import File
import re
from django.shortcuts import render
from django.views import View
from django.views.generic import ListView, CreateView
from analysis_app.forms import UploadForm, CreateUserForm, EightyEightForm
from analysis_app.models import (PlayerNames, PlayerScoresMinutes, SeasonFixtures, NormScores,
                         PlayerProfileScores, SingleFixture)
from analysis_app.player_list.player_list_and_profile_funcs import doubebarrel_conversion
from analysis_app.main88 import call_single_88, agg_single_gw
from analysis_app.main_predictor import (get_names, get_minutes, fixture_amplifier, predict_gameweek, predict_gw_01,
                                 predict_gw_02, predict_gw_03, predict_gw_04, predict_gw_05, predict_gw_06_09,
                                 predict_gw_10_plus)
from django.forms.models import model_to_dict
import pandas as pd
import numpy as np


def index(request):
    return render(request, "switcher.html")


def registerPage(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()

    context = {'form': form}
    return render(request, 'register.html', context)


def loginPage(request):
    context = {}
    return render(request, 'login.html', context)


class PlayerListView(ListView):
    template_name = 'player_list.html'
    model = PlayerNames

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ScorePredictorView(View):
    template_name = 'score_predictor_landing.html'

    def get(self, request):
        return render(request, self.template_name)


class SinglePlayerView(View):
    template_name = "single_player_view.html"

    def get(self, request):
        return render(request, self.template_name)


class SeasonFixturesView(ListView):
    template_name = 'season_fixtures.html'
    model = SeasonFixtures

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ScorePredictorOverviewView(View):
    template_name = 'score_predictor_overview.html'
    model = PlayerScoresMinutes

    def get(self, request):
        scores_df = get_names()
        minutes_df = get_minutes()
        predicted_gameweek = predict_gameweek(scores_df, minutes_df)
        # predict_gw_01(predicted_gameweek)
        predict_gw_02(predicted_gameweek)
        predict_gw_03(predicted_gameweek)
        predict_gw_04(predicted_gameweek)
        predict_gw_05(predicted_gameweek)
        predict_gw_06_09(predicted_gameweek, 6)
        predict_gw_06_09(predicted_gameweek, 7)
        predict_gw_06_09(predicted_gameweek, 8)
        predict_gw_06_09(predicted_gameweek, 9)

        for i in range(10, 18):
            predict_gw_10_plus(predicted_gameweek, i)

        context = {'scores': scores_df}  # Returns first
        return render(request, self.template_name, context)


class EightyEightLandingView(View):
    template_name = 'eighty_eight_landing.html'

    def get(self, request):

        return render(request, self.template_name)


class EightyEightSingleView(View):
    template_name = 'eighty_eight_single.html'
    model = PlayerNames

    def get(self, request):
        teams = call_single_88(25, 29, 8)
        context = {'teams': teams[0]}  # Returns first

        return render(request, self.template_name, context)


class EightyEightAggView(View):
    template_name = 'eighty_eight_agg.html'
    model = PlayerNames

    def get(self, request):
        eighty_eight_single = call_single_88(20, 29, 8)  # First GW, Last GW, No. of teams per gameweeks.
        print(eighty_eight_single)
        aggregates = agg_single_gw(eighty_eight_single[0], eighty_eight_single[1],
                                   eighty_eight_single[2], eighty_eight_single[3])
        print('AGG TYPE', aggregates)
        context = {'aggs': aggregates}

        return render(request, self.template_name, context)


class NormScoreView(ListView):
    template_name = 'norm_score.html'
    model = NormScores

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class PlayerInfoView(View):
    template_name = 'player_profile.html'
    model = PlayerNames
    data = PlayerProfileScores

    def get(self, request, *args, **kwargs):
        a = request.build_absolute_uri()
        name_from_url = re.findall(r'(?<=profile\/).*', a)
        image_src = '/static/profile_pics/' + name_from_url[0] + '.png'
        split_names = name_from_url[0].split('-')
        full_name = ''

        for i, split in enumerate(split_names):
            split = split.capitalize()
            if i == 0:
                full_name = split
            else:
                full_name = full_name + ' ' + split

        full_name = doubebarrel_conversion(full_name)

        print(full_name, flush=True)
        player_qs = self.model.objects.filter(name=full_name).values()
        scores_qs = self.data.objects.filter(name=full_name).values()
        scores_df = pd.DataFrame.from_records(scores_qs)
        print(scores_df, flush=True)
        context = {'player_name': player_qs[0]['name'], 'team': player_qs[0]['team'],
                   'position': player_qs[0]['position'], 'image_src': image_src, 'object_list': scores_df}

        return render(request, self.template_name, context)


class EightyEightFormView(View):
    template_name = 'eighty_eight_form.html'
    form_class = EightyEightForm
    request = ''
    initial = {'key', 'value'}

    def get(self, request, *args, **kwargs):
        eighty_eight_form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'ee_form': eighty_eight_form})

    def post(self, request, *args, **kwargs):
        eighty_eight_form = self.form_class(request.POST or None)
        eighty_eight_form.non_field_errors()
        field_errors = [(field.label, field.errors) for field in eighty_eight_form]
        print('field errors:', field_errors)
        if eighty_eight_form.is_valid():
            print('valid:', eighty_eight_form.cleaned_data)
            ee_inputs = eighty_eight_form.cleaned_data
            print(ee_inputs)
            teams = call_single_88(ee_inputs)


class SingleFixtureView(View):
    template_name = 'single_fixture.html'
    model = SingleFixture
    data = PlayerProfileScores

    def get(self, request, *args, **kwargs):
        scores_qs = self.data.objects.values()
        scores_df = pd.DataFrame.from_records(scores_qs)
        print(scores_df, flush=True)
        context = {'object_list': scores_df}

        return render(request, self.template_name, context)
