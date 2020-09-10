from django.conf import settings
from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from core.views import (
    PlayerListView,
    ScorePredictorView,
    TeamRankingsView,
    SeasonFixturesView,
    ScorePredictorOverviewView,
    EightyEightLandingView,
    EightyEightSingleView,
    EightyEightAggView,
    index
)

app_name = 'core'

urlpatterns = [
    path('', index, name='switcher'),
    path('player_list/', PlayerListView.as_view(), name='player_list'),
    path('theeigthyeight/', EightyEightLandingView.as_view(), name='theeightyeight'),
    path('theeigthyeight/single88', EightyEightSingleView.as_view(), name='single88'),
    path('theeigthyeight/agg88', EightyEightAggView.as_view(), name='agg88'),

    path('score_predictor/', ScorePredictorView.as_view(), name='score_predictor'),
    path('score_predictor/rankings/', TeamRankingsView.as_view(), name='rankings'),
    path('score_predictor/season_fixtures/', SeasonFixturesView.as_view(), name='season_fixtures'),
    path('score_predictor/browse-by-club/', ScorePredictorOverviewView.as_view(), name='browse_club')
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
