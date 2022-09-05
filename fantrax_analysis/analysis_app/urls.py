from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from analysis_app.views import (
    PlayerListView,
    PlayerInfoView,
    ScorePredictorView,
    SeasonFixturesView,
    SingleFixtureView,
    ScorePredictorOverviewView,
    EightyEightLandingView,
    EightyEightFormView,
    EightyEightSingleView,
    EightyEightAggView,
    NormScoreView,
    index,
    loginPage,
    registerPage,
)

app_name = 'analysis_app'

urlpatterns = [
    path('', index, name='switcher'),
    path('register/', registerPage, name='register'),
    path('login/', loginPage, name='login'),


    path('player_list/', PlayerListView.as_view(), name='player_list'),
    path('player_list/player-profile/<slug:slug>', PlayerInfoView.as_view(), name='player_profile'),

    path('theeigthyeight/', EightyEightLandingView.as_view(), name='theeightyeight'),
    path('theeigthyeight/form', EightyEightFormView.as_view(), name='theeightyeightform'),
    path('theeigthyeight/single88', EightyEightSingleView.as_view(), name='single88'),
    path('theeigthyeight/agg88', EightyEightAggView.as_view(), name='agg88'),

    path('score_predictor/', ScorePredictorView.as_view(), name='score_predictor'),
    path('score_predictor/season_fixtures/', SeasonFixturesView.as_view(), name='season_fixtures'),
    path('score_predictor/season_fixtures/<slug:slug>', SingleFixtureView.as_view(), name='single_fixture'),
    path('score_predictor/browse-by-club/', ScorePredictorOverviewView.as_view(), name='browse_club'),

    path('norm_score/', NormScoreView.as_view(), name='norm_score'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
