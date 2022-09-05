import pandas as pd
import numpy as np
from analysis_app.The88.functions88 import call_gameweeks, team_creator
from analysis_app.models import PlayerNames


def call_single_88(ee_inputs):
    first_gameweek = ee_inputs[1]
    last_gameweek = ee_inputs[2]
    number_of_team_per_gw = ee_inputs[3]
    # variables for testing:
    '''first_gameweek = 1
    last_gameweek = 5
    number_of_team_per_gw = 8'''

    # where we define out is the GW scope we want in our 88:
    # my_gameweeks is a dictionary of gameweek data as taken from individual csv files
    my_gameweeks = call_gameweeks(first_gameweek, last_gameweek)

    # TODO: 8 should be dynamic, to be entered by the user
    team_numbers = np.arange(number_of_team_per_gw, 0, -1)
    teams = []
    for key in my_gameweeks:
        team = team_creator(my_gameweeks[key], team_numbers)
        teams.append(team)

    return [teams, first_gameweek, last_gameweek, team_numbers]


def agg_single_gw(teams, first_gameweek, last_gameweek, team_numbers):
    '''
    Input is a team gw in a single_gameweek layout.
    This is converted
    :param teams:
    :param first_gameweek:
    :param last_gameweek:
    :param team_numbers:
    :return:
    '''
    gws = np.arange(first_gameweek, last_gameweek+1, 1)

    one_column_teams = []
    for i, single_week in enumerate(teams):
        one_column_team = pd.DataFrame(columns=['name', 'GW_{0}'.format(gws[i])])
        for column in single_week.columns:
            for row in single_week[column]:
                one_column_team = one_column_team.append({'name': row}, ignore_index=True)
        one_column_teams.append(one_column_team)


    # TODO: 8 should be dynamic, to be entered by the user
    qs = PlayerNames.objects.values_list('name', 'team', 'position')
    agg_88 = pd.DataFrame(list(qs), columns=['name', 'team', 'position'])
    dfs = [agg_88]
    for entry in one_column_teams:
        k = 0
        for j in team_numbers:
            entry.iloc[k: k + 11, 1] = j
            k = k + 11
        dfs.append(entry)

    from functools import reduce
    complete_agg = reduce(lambda left, right: pd.merge(left, right, on='name', how='outer'), dfs)

    complete_agg.fillna(0, inplace=True)

    number_of_gameweeks = last_gameweek + 1 - first_gameweek
    weights = np.arange(1, number_of_gameweeks + 1, 1)
    agg_sub_df = complete_agg.drop(['name', 'team', 'position'], axis=1)
    complete_agg['Total'] = agg_sub_df.dot(weights)

    complete_agg = complete_agg.sort_values(by='Total', ascending=False)

    return complete_agg
