import pandas as pd
import numpy as np
from datetime import datetime


minute_data = pd.read_csv('minute_data/combined_minute_data_2019_20.csv')
distributions = pd.read_csv('distributions.csv')
opening_predictions = pd.read_csv('initial_conditions_last_year.csv.csv')
fivethirtyeight = pd.read_csv('fixtures.csv')

player_predictions = pd.DataFrame(columns=['Date', 'GW', 'Player', 'Position', 'Team', 'Opp', 'Start', 'Min', 'FPts',
                                           'NormScore', 'RawPred', 'FT8', 'OppAdj', 'Pred'])

player_predictions[['Date', 'Player', 'Position', 'Team', 'Opp', 'Min', 'FPts']] = \
    minute_data[['date', 'player', 'position', 'team', 'opp', 'min', 'fpts']]

player_predictions['FPts'] = player_predictions['FPts'].astype(float)
player_predictions['Min'] = player_predictions['Min'].astype(str)


def get_norm_score(distributions, x):
    act_fpts = x['FPts']
    minutes = x['Min']

    if minutes == '90':
        norm_score = act_fpts
    else:
        distributions = distributions[(distributions['minutes_played'].astype(str) == minutes)
                                      & (distributions['actual_score'].astype(float) <= act_fpts)]
        if distributions.empty:
            norm_score = 0
        else:
            last_row = len(distributions.index) - 1
            norm_score = distributions.reset_index(drop=True).loc[last_row, 'extrapolated_score']

    return norm_score


player_predictions['NormScore'] = player_predictions.apply(lambda x: get_norm_score(distributions, x), axis=1)

player_predictions['Date'] = player_predictions['Date'].str.replace('-', '')
player_predictions['Date'] = player_predictions['Date'].str.replace('Apr', 'April')
player_predictions['Date'] = player_predictions['Date'].str.replace('Mar', 'March')
player_predictions['Date'] = player_predictions['Date'].str.replace('Feb', 'February')
player_predictions['Date'] = player_predictions['Date'].str.replace('Jan', 'January')
player_predictions['Date'] = player_predictions['Date'].str.replace('Dec', 'December')
player_predictions['Date'] = player_predictions['Date'].str.replace('Nov', 'November')
player_predictions['Date'] = player_predictions['Date'].str.replace('Oct', 'October')
player_predictions['Date'] = player_predictions['Date'].str.replace('Sep', 'September')
player_predictions['Date'] = player_predictions['Date'].str.replace('Aug', 'August')
player_predictions['Date'] = pd.to_datetime(player_predictions['Date'], format='%B%d').dt.strftime('%B%d')

start_date = ['May20', 'May13', 'May06', 'April29', 'April22', 'April15', 'April08', 'April01', 'March18', 'March11',
              'March04', 'February25', 'February18', 'February11', 'February08', 'January21', 'January14', 'December31',
              'December28', 'December25', 'December17', 'December14', 'December10', 'December03', 'November30',
              'November26', 'November19', 'November05', 'October29', 'October22', 'October15', 'October01',
              'September24', 'September17', 'September10', 'August27', 'August20', 'August13']

end_date = ['May22', 'May19', 'May12', 'May05', 'April28', 'April21', 'April14', 'April07', 'March31',
            'March17', 'March10', 'March03', 'February24', 'February17', 'February10', 'February07', 'January20',
            'January13', 'December30', 'December27', 'December24', 'December16', 'December13', 'December09',
            'December02', 'November29', 'November25', 'November18', 'November04', 'October28', 'October21', 'October14',
            'September30', 'September23', 'September16', 'September09', 'August26', 'August19']


def obtain_gw_from_date(x, start_date, end_date):

    x['Date'] = pd.to_datetime(x['Date'], format='%B%d')

    for i, date in enumerate(start_date):
        date = datetime.strptime(date, '%B%d')
        x.loc[(x['Date'] >= date) & (x['Date'] <= datetime.strptime(end_date[i], '%B%d')), 'GW'] = 38 - i

    x['Date'] = x['Date'].dt.strftime('%B%d')

    return x


def obtain_gw_1_pred(player_predictions, opening_predictions):

    min_gw_per_player = player_predictions.groupby('Player')['GW'].min().reset_index()
    player_predictions = player_predictions.merge(opening_predictions, on='Player', how='outer')

    for i, row in min_gw_per_player.iterrows():
        player_predictions.loc[(player_predictions['Player'] == row['Player']) &
                               (player_predictions['GW'] == row['GW']), 'RawPred'] = player_predictions['OpScore']

    return player_predictions


player_predictions = obtain_gw_from_date(player_predictions, start_date, end_date)
player_predictions.to_csv('investment_grade/player_profile_scores_s.csv')
player_predictions = obtain_gw_1_pred(player_predictions, opening_predictions)
unique_players = player_predictions['Player'].unique()


for player in unique_players:
    my_player = player_predictions[player_predictions['Player'] == player].reset_index()
    last_row = len(my_player.index) - 1
    for i in range(0, last_row + 1):
        if i == last_row:
            pass
        elif i == last_row - 1:
            my_player.loc[i, 'RawPred'] = (4*my_player.loc[i, 'OpScore'] + my_player.loc[last_row, 'FPts'])/5
        elif i == last_row - 2:
            my_player.loc[i, 'RawPred'] = (3*my_player.loc[i, 'OpScore'] + my_player.loc[last_row, 'FPts']
                                           + my_player.loc[last_row - 1, 'FPts'])/5
        elif i == last_row - 3:
            my_player.loc[i, 'RawPred'] = (2*my_player.loc[i, 'OpScore'] + my_player.loc[last_row, 'FPts']
                                           + my_player.loc[last_row - 1, 'FPts']
                                           + my_player.loc[last_row - 2, 'FPts'])/5
        elif i == last_row - 4:
            my_player.loc[i, 'RawPred'] = (my_player.loc[i, 'OpScore'] + my_player.loc[last_row, 'FPts']
                                           + my_player.loc[last_row - 1, 'FPts']
                                           + my_player.loc[last_row - 2, 'FPts']
                                           + my_player.loc[last_row - 3, 'FPts']) / 5
        else:
            my_player.loc[i, 'RawPred'] = (my_player.loc[i+1, 'FPts'] + my_player.loc[i+2, 'FPts']
                                           + my_player.loc[i+3, 'FPts']
                                           + my_player.loc[i+4, 'FPts']
                                           + my_player.loc[i+5, 'FPts']) / 5

    my_player = my_player.set_index('index')
    player_predictions.loc[(player_predictions['Player'] == player), 'RawPred'] = my_player['RawPred']


def obtain_fivethirtyeight(x, fivethirtyeight):
    '''
    Adds 538 predictions for each game
    :param player_predictions: df
    :param fivethirtyeight: csv
    :return:
    '''

    gw = x['GW']

    try:
        if x['Opp'][0] == '@':
            away_team = x['Team']
            home_team = x['Opp'][1:]
            my_538 = fivethirtyeight[(fivethirtyeight['GW'] == gw) & (fivethirtyeight['Home'] == home_team) & (
                    fivethirtyeight['Away'] == away_team)].reset_index()
            bump = my_538.loc[0, 'A_538']
        else:
            home_team = x['Team']
            away_team = x['Opp']
            my_538 = fivethirtyeight[(fivethirtyeight['GW'] == gw) & (fivethirtyeight['Home'] == home_team) & (
                fivethirtyeight['Away'] == away_team)].reset_index()
            bump = my_538.loc[0, 'H_538']

        return bump

    except TypeError:
        print('CRAPPING OUT WITH THIS MAN', x['Player'])
        x['FT8'] = np.nan


def calc_return(x):
    '''
    Calculates the return on investment, only if they were investment grade (12+ pred)
    :param x: dataframe row
    :return:
    '''
    if x['Pred'] >= 12:
        x = x['FPts'] - 12
    else:
        x = 0

    return x


player_predictions['FT8'] = player_predictions.apply(lambda x: obtain_fivethirtyeight(x, fivethirtyeight), axis=1)
player_predictions['OppAdj'] = player_predictions['FT8'] - 33
player_predictions['Pred'] = player_predictions['RawPred'] + player_predictions['OppAdj']/10
player_predictions['Return'] = player_predictions.apply(lambda x: calc_return(x), axis=1)
player_predictions = player_predictions.sort_values(by=['Team', 'Player', 'GW'], ascending=True)
player_predictions['CumReturn'] = player_predictions.groupby('Player')['Return'].cumsum()
player_predictions['CumReturn'] = player_predictions['CumReturn'].shift(1, fill_value=0)
player_predictions['Start'] = 0

print(player_predictions.columns)

for i, row in player_predictions.iterrows():
    if i == 0:
        row['CumReturn'] = 0
    elif player_predictions.iloc[i, 2] != player_predictions.iloc[i-1, 2]:
        player_predictions.at[i, 18] = 0
    else:
        pass

player_predictions.to_csv('investment_grade/player_predictions.csv')

for gw in range(1, 39):
    investment_gw = player_predictions.loc[(player_predictions['GW'] == gw) & (player_predictions['Pred'] >= 12), :]
    investment_gw.to_csv('investment_grade/invest_gw' + str(gw) + '.csv')
