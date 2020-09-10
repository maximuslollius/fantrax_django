from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import ListView
from core.forms import UploadForm
from core.models import PlayerNames, PlayerScores, PredictedTable, SeasonFixtures, FirstWeekPred
from core.main88 import call_single_88, agg_single_gw
from core.main_predictor import (get_names, get_minutes, fixture_amplifier, predict_gameweek, predict_gw_01,
                                 predict_gw_02, predict_gw_03, predict_gw_04, predict_gw_05, predict_gw_06_09,
                                 predict_gw_10_plus)
import pandas as pd
import numpy as np

def index(request):
    return render(request, "switcher.html")


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


class TeamRankingsView(ListView):
    template_name = 'rankings.html'
    model = PredictedTable

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class SeasonFixturesView(View):
    template_name = 'season_fixtures.html'
    model = SeasonFixtures

    def get(self, request, *args, **kwargs):
        fixtures_df = fixture_amplifier()

        context = {
            'dataframe': fixtures_df,
        }

        return render(request, self.template_name, context)


class ScorePredictorOverviewView(View):
    template_name = 'score_predictor_overview.html'
    model = PlayerScores

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
        teams = call_single_88()
        context = {'teams': teams[0]}  # Returns first

        return render(request, self.template_name, context)


class EightyEightAggView(View):
    template_name = 'eighty_eight_agg.html'
    model = PlayerNames

    def get(self, request):
        eighty_eight_single = call_single_88(1, 5, 8)
        aggregates = agg_single_gw(eighty_eight_single[0], eighty_eight_single[1],
                                   eighty_eight_single[2], eighty_eight_single[3])
        context = {'aggs': aggregates}

        return render(request, self.template_name, context)
