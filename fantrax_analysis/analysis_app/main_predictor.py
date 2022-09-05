import pandas as pd
import numpy as np
# from core.predicotr.predictor_functions import gw_pred_one
from core.models import PlayerScores, FirstWeekPred, PredictedTable, SeasonFixtures
import os
from core.main88 import call_single_88, agg_single_gw
import decimal


def get_names():
    '''
    Returns the names and basic (actual) scores from PlayerScores module.
    :return: scored_df
    '''
    # Convert our two backends to df for manipulation
    from django_pandas.io import read_frame
    # read in the models required
    scores_qs = PlayerScores.objects.all()
    scores_df = read_frame(scores_qs)
    pred_01_qs = FirstWeekPred.objects.all()
    pred_01_df = read_frame(pred_01_qs)

    # add week 1 predictions to the scores:
    scores_df = pd.merge(scores_df, pred_01_df, on='name', how='outer').fillna(0)

    scores_df = scores_df[['name', 'team', 'position', 'pred_01', 'gw_01', 'gw_02', 'gw_03', 'gw_04', 'gw_05', 'gw_06',
                           'gw_07', 'gw_08', 'gw_09', 'gw_10', 'gw_11', 'gw_12', 'gw_13', 'gw_14', 'gw_15', 'gw_16',
                           'gw_17', 'gw_18', 'gw_19', 'gw_20', 'gw_21', 'gw_22', 'gw_23', 'gw_24', 'gw_25', 'gw_26',
                           'gw_27', 'gw_28', 'gw_29']]

    scores_df.sort_values(by=['team', 'position'])

    return scores_df


def get_minutes():
    '''
    Create a minutes played dataframe from the scraped .csv Transfermarkt files
    :return: dataframe
    '''

    # set up the path the minutes folder where we have scraped our data from Transfermarkt:
    path_to_minutes_folder = os.path.join(os.getcwd(), 'core', 'scrapes', 'minutes_from_dict')

    #
    list_of_filenames = []
    player_minutes = ['name']
    gws = [str(i) for i in range(1, 30)]
    player_minutes.append(gws)

    # set up final dataframe, create list of names in file so we can loop through alphabetically, this is preferrable
    # for de-bugging:
    all_player_minutes = pd.DataFrame(columns=['Transfermarkt_name'])
    names_in_file = []
    for filename in os.listdir(path_to_minutes_folder):
        names_in_file.append(filename)
        names_in_file.sort()

    # remove dud file, not compatible with UTF-8
    # names_in_file.remove('.DS_Store')

    # loop through the files in minutes folder, create subset df with relevant data. Pivot on name to convert minutes to
    # columnar format for final merge:
    for filename in names_in_file:
        path_to_file = os.path.join(os.getcwd(), 'core', 'scrapes', 'minutes_from_dict', filename)
        with open(path_to_file) as f:
            list_of_filenames.append(f)
            minutes_df = pd.read_csv(f)
            minutes_df = minutes_df[['Player', 'Matchday', 'Minutes']]
            renamer = {'Player': 'Transfermarkt_name', 'Matchday': 'gw', 'Minutes': 'minutes'}
            minutes_df.rename(columns=renamer, inplace=True)
            minutes_df.dropna(inplace=True)

            for index, row in minutes_df.iterrows():
                if '\'' in row['minutes']:
                    pass
                else:
                    minutes_df = minutes_df.drop(index)
            minutes_pivot = pd.pivot(minutes_df, index='Transfermarkt_name', columns='gw', values='minutes')
            minutes_df = pd.DataFrame(minutes_pivot.to_records())
            all_player_minutes = all_player_minutes.append(minutes_df)

    def renaming_col(col):
        '''
        Renames minute columns to have minute prefix.
        :param col:
        :return: col
        '''
        for i in range(1, 39):
            if i < 10:
                if col == str(i):
                    col = "min_0" + col
                else:
                    pass
            else:
                if col == str(i):
                    col = "min_" + col
                else:
                    pass
        return col

    all_player_minutes.columns = [renaming_col(col) for col in all_player_minutes]

    all_player_minutes = all_player_minutes.loc[:, ~all_player_minutes.columns.str.contains('\\.', case=False)]
    all_player_minutes = all_player_minutes[all_player_minutes.columns.sort_values(ascending=True)]

    for col in all_player_minutes[all_player_minutes.filter(like='min').columns].columns:
        all_player_minutes[col].fillna(0)
        all_player_minutes[col] = all_player_minutes[col].apply(lambda x: 0 if pd.isna(x) else int(x[:-1]))

    all_player_minutes.to_csv('all_player_minutes.csv')
    return all_player_minutes


def fixture_amplifier():
    '''
    calls the PredictedTable database, and assigns match types (amplifiers) to each game.
    :return: fixtures_df dataframe.
    '''
    # Convert our two backends to df for manipulation
    from django_pandas.io import read_frame
    table_qs = PredictedTable.objects.all()
    table_df = read_frame(table_qs)
    fixtures_qs = SeasonFixtures.objects.all()
    fixtures_df = read_frame(fixtures_qs)
    fixtures_df['type_home'] = 0
    fixtures_df['type_away'] = 0

    # returns the predicted table for a given gameweek. (e.g. range (2,3) returns gameweek 1.
    # then we populate home and away types from the predicted_Table

    # TODO: k should be updated each gameweek, each time 538 have a new predicted table
    for k in range(1, 30):  # k range is the number of gameweeks we can run
        for i in range(k + 1, k + 2):  # i will ensure the task is completed for a single gameweek
            for index, row in fixtures_df.iterrows():
                if row['gameweek'] == i - 1:
                    table_4_week = list(table_df.iloc[:, i])

                    fixtures_df.at[index, 'type_home'] = float(table_4_week.index(row['home_team']) + 1)
                    fixtures_df.at[index, 'type_away'] = float(table_4_week.index(row['away_team']) + 1)

    # populate amplifier and match_type columns
    fixtures_df['home_amp'] = round((fixtures_df['type_away'] - fixtures_df['type_home']) / 4 + 0.4)
    fixtures_df['away_amp'] = round((fixtures_df['type_home'] - fixtures_df['type_away']) / 4 - 0.4)
    fixtures_df['match'] = fixtures_df['home_team'] + fixtures_df['away_team']
    fixtures_df['match_type'] = fixtures_df['home_amp'].astype(str).replace('\.0', '', regex=True) + '__' + \
                                fixtures_df['away_amp'].astype(str).replace('\.0', '', regex=True)

    return fixtures_df


def predict_gameweek(scores_df, all_player_minutes):
    '''
    Merge minute and past score data, and
    :param scores_df: a dataframe containing
    :param all_player_minutes:
    :return:
    '''

    # read in mapping, convert Transfermarkt names from minutes data to names from Fantrax:
    mapping_names = pd.read_csv('./core/fixtures/predicted_league_tables/mapping.csv')
    all_player_minutes = pd.merge(all_player_minutes, mapping_names, on='Transfermarkt_name', how='left')
    all_player_minutes.drop(columns='Transfermarkt_name', inplace=True)

    predicted_gameweek = pd.merge(scores_df, all_player_minutes, on='name', how='outer')

    # Manually add Position & Team to those sold in January
    predicted_gameweek = insert_leavers(predicted_gameweek)

    # rename gameweeks 1-9 in fixtures so they align with predicted_gameweek df:
    fixtures_df = fixture_amplifier()
    gw_renamer = {'1': '01', '2': '02', '3': '03', '4': '04', '5': '05', '6': '06',
                  '7': '07', '8': '08', '9': '09'}
    fixtures_df['gameweek'] = fixtures_df['gameweek'].astype(str)
    fixtures_df.replace(gw_renamer, inplace=True)

    # initialise the gameweek opponent amplifier in the dataframe:
    for col in predicted_gameweek.columns:
        if 'gw' in str(col):
            stringed_col = str(col)
            stringed_col = stringed_col[-2:]
            for i, row in fixtures_df.iterrows():
                if row['gameweek'] == stringed_col:
                    predicted_gameweek['amp_{0}'.format(row['gameweek'])] = 0

    # update the gameweek opponent amplifier in the dataframe:
    for col in predicted_gameweek.columns:
        if 'gw' in str(col):
            stringed_col = str(col)
            stringed_col = stringed_col[-2:]
            for i, row in fixtures_df.iterrows():
                if row['gameweek'] == stringed_col:
                    for k, entry in predicted_gameweek.iterrows():
                        if entry['team'] == row['home_team']:
                            predicted_gameweek.at[k, 'amp_{0}'.format(row['gameweek'])] = row['home_amp']
                        elif entry['team'] == row['away_team']:
                            predicted_gameweek.at[k, 'amp_{0}'.format(row['gameweek'])] = row['away_amp']
                        else:
                            pass


    # Order column by gameweek cluster (e.g. by column-name suffix)
    predicted_gameweek = predicted_gameweek[sorted(predicted_gameweek.columns, key=lambda x: x[-2:])]

    gameweeks_string = fixtures_df['gameweek'].sort_values().unique()

    # TODO: hard coded at 16 gameweek for test
    up_until_gw = 30
    for element in gameweeks_string:
        if int(element) < up_until_gw:
            mask_above_45 = predicted_gameweek['min_{0}'.format(element)] > 45
            mask_above_15 = predicted_gameweek['min_{0}'.format(element)] > 15
            mask_above_5 = predicted_gameweek['min_{0}'.format(element)] > 5
            mask_above_1 = predicted_gameweek['min_{0}'.format(element)] > 1
            mask_0 = predicted_gameweek['min_{0}'.format(element)] < 1
            mask_null = predicted_gameweek['min_{0}'.format(element)].isnull()

            predicted_gameweek.loc[mask_above_45,
                                   'gw_{0}'.format(element)] = predicted_gameweek['gw_{0}'.format(element)]/ \
                                                                     (predicted_gameweek['min_{0}'.format(element)]/90)
            # Player has played 16-45 mins: still divide by 90 but maximum extrapolated points is 20
            predicted_gameweek.loc[(~mask_above_45) & mask_above_15,
                                    'gw_{0}'.format(element)] = predicted_gameweek['gw_{0}'.format(element)] / \
                                                                (predicted_gameweek['min_{0}'.format(element)]/90)

            predicted_gameweek.loc[(~mask_above_45) & mask_above_15, 'gw_{0}'.format(element)] = \
                predicted_gameweek.loc[(~mask_above_45) & mask_above_15, 'gw_{0}'.format(element)]\
                    .apply(lambda x: x if x < 20 else 20)

            # Player has played 6-15 mins: divide by 45 but maximum extrapolated points is 15
            predicted_gameweek.loc[(~mask_above_15) & mask_above_5,
                                    'gw_{0}'.format(element)] = predicted_gameweek['gw_{0}'.format(element)] / \
                                                                (predicted_gameweek['min_{0}'.format(element)]/45)

            predicted_gameweek.loc[(~mask_above_15) & mask_above_5, 'gw_{0}'.format(element)] = \
                predicted_gameweek.loc[(~mask_above_15) & mask_above_5, 'gw_{0}'.format(element)]\
                    .apply(lambda x: x if x < 15 else 15)

            # Player has played 2-5 mins: divide by 30 but maximum extrapolated points is 10
            predicted_gameweek.loc[(~mask_above_5) & mask_above_1,
                                   'gw_{0}'.format(element)] = predicted_gameweek['gw_{0}'.format(element)] / \
                                                               (predicted_gameweek['min_{0}'.format(element)]/30)

            predicted_gameweek.loc[(~mask_above_5) & mask_above_1, 'gw_{0}'.format(element)] = \
                predicted_gameweek.loc[(~mask_above_5) & mask_above_1, 'gw_{0}'.format(element)]\
                    .apply(lambda x: x if x < 10 else 10)

            # Player has played 1 min: divide by 15 but maximum extrapolated points is 8
            predicted_gameweek.loc[~mask_above_1,
                                   'gw_{0}'.format(element)] = predicted_gameweek['gw_{0}'.format(element)] / \
                                                                (predicted_gameweek['min_{0}'.format(element)]/15)

            predicted_gameweek.loc[~mask_above_1, 'gw_{0}'.format(element)] = \
                predicted_gameweek.loc[~mask_above_1, 'gw_{0}'.format(element)].apply(lambda x: x if x < 8 else 8)

            predicted_gameweek.loc[mask_0, 'gw_{0}'.format(element)] = 0
            predicted_gameweek.loc[mask_null, 'gw_{0}'.format(element)] = 0
            predicted_gameweek.loc[mask_null, 'min_{0}'.format(element)] = 0

            # Round the digits to two deimal places
            predicted_gameweek['gw_{0}'.format(element)] = predicted_gameweek['gw_{0}'.format(element)].round(2)

    predicted_gameweek = predicted_gameweek[predicted_gameweek['position'] != '0']

    predicted_gameweek.to_csv('predicted_gw.csv')

    return predicted_gameweek


def insert_leavers(predicted_gameweek):
    '''
    Manually inserts clubs and positions of those who have now left the league
    :param predicted_gameweek:
    :return:
    '''

    dict_of_leavers = {'Angelino': ['MCI', 'D'], 'Ashley Young': ['MUN', 'D'], 'Brandon Pierrick': ['CRY', 'M'],
                       'Callum Robinson': ['SHU', 'F'], 'Chicharito': ['WHU', 'F'], 'Christian Eriksen': ['TOT', 'M'],
                       'Connor Wickham': ['CRY', 'F'], 'Dennis Srbeny': ['NOR', 'F'], 'Dimitri Foulquier': ['WAT', 'D'],
                       'Emile Smith Rowe': ['ARS', 'M'], 'Florin Andone': ['BHA', 'F'], 'Gaetan Bong': ['BHA', 'D'],
                       'Georges-Kevin Nkoudou': ['TOT', 'M'], 'Henrikh Mkhitaryan': ['ARS', 'M'],
                       'Ibrahim Amadou': ['NOR', 'D,M'], 'Jesus Vallejo': ['WOL', 'D,M'],
                       'Jonathan Kodjia': ['AVL', 'F'], 'Ki Sung-Yueng': ['NEW', 'M'], 'Marcos Rojo': ['MUN', 'D'],
                       'Max Kilman': ['WOL', 'D'], 'Maya Yoshida': ['SOU', 'D'], 'Nacho Monreal': ['ARS', 'D'],
                       'Nathan Holland': ['WHU', 'M'], 'Patrick Cutrone': ['WOL', 'F'], 'Patrick Roberts': ['NOR', 'F'],
                       'Ravel Morrison': ['SHU', 'M'], 'Roberto Jimenez': ['WHU', 'G'], 'Sebastian Prodl': ['WAT', 'D'],
                       'Victor Camarasa': ['CRY', 'M'], 'Cedric Soares (prior)': ['SOU', 'D'],
                       'Danny Rose (prior)': ['TOT', 'D,M'], 'Ryan Bennett (prior)': ['WOL', 'D'],
                       'Tariq Lamptey (prior)': ['CHE', 'D'], 'Danny Drinkwater (prior)': ['BUR', 'M'],
                       'Cenk Tosun (prior)': ['EVE', 'F'], 'Kyle Walker-Peters (prior)': ['TOT', 'D']
                       }

    for k, v in dict_of_leavers.items():
        mask = predicted_gameweek['name'] == k
        predicted_gameweek.loc[mask, 'team'] = v[0]
        predicted_gameweek.loc[mask, 'position'] = v[1]

    return predicted_gameweek


def predict_gw_01(predicted_gameweek):
    '''Predicts Gameweek 1
    param: predicted_gameweek'''

    predicted_gw_01 = pd.DataFrame(columns=['G'])
    predicted_gameweek = predicted_gameweek[['name', 'position', 'team', 'pred_01', 'amp_01']].fillna(0)
    gw_01_goalkeepers = predicted_gameweek[predicted_gameweek['position'] == 'G']
    gw_01_goalkeepers.sort_values(by=['pred_01'], ascending=False, inplace=True)
    predicted_gw_01['G'] = gw_01_goalkeepers['name'].head(70)

    gw_01_defenders = predicted_gameweek[predicted_gameweek['position'].str.contains('D', na=False)]
    gw_01_defenders.sort_values(by=['amp_01', 'pred_01'], ascending=False, inplace=True)
    print(gw_01_defenders['team'].unique())
    predicted_gw_01['D'] = list(gw_01_defenders['name'].head(70))

    gw_01_mids_fwds = predicted_gameweek[predicted_gameweek['position'].str.contains('M|F', na=False)]
    gw_01_mids_fwds.sort_values(by=['pred_01'], ascending=False, inplace=True)
    predicted_gw_01['M, F'] = list(gw_01_mids_fwds['name'].head(70))

    predicted_gw_01.to_csv('predicted_gw_01.csv')


def predict_gw_02(predicted_gameweek):
    '''Predicts Gameweek 2
    param: predicted_gameweek'''

    # STEP 1(a): get the % diff between predicted and actual for the prior gameweek
    predicted_gameweek.loc[predicted_gameweek['min_01'] == 0, 'gw_01'] = predicted_gameweek['pred_01']

    predicted_gameweek['diff_01'] = (predicted_gameweek['gw_01']-predicted_gameweek['pred_01']) / predicted_gameweek['pred_01']
    predicted_gameweek['diff_01'].replace([np.inf, -np.inf], 0, inplace=True)
    predicted_gameweek['diff_01'].clip(upper=1, axis=0, inplace=True)

    # STEP 1(b): Create prediction for second week:
    predicted_gameweek['pred_02'] = ((predicted_gameweek['gw_01'] - predicted_gameweek['amp_01'])
                                     + predicted_gameweek['amp_02'])*(1 + (predicted_gameweek['diff_01'] / 5))

    predicted_gameweek = predicted_gameweek[sorted(predicted_gameweek.columns, key=lambda x: x[-2:])]

    # STEP 2: List Investment Level Goalkeepers
    gw_02_goalkeepers = predicted_gameweek[predicted_gameweek['position'] == 'G']

    gw_02_goalkeepers['confidence_01'] = 0

    gw_02_goalkeepers.loc[((gw_02_goalkeepers['pred_01'] <= 12) & (gw_02_goalkeepers['gw_01'] <= 12)) |
        ((gw_02_goalkeepers['pred_01'] >= 12) & (gw_02_goalkeepers['gw_01'] >= 12)), 'confidence_01'] = 1

    gw_02_goalkeepers['INVEST'] = 'NO'
    gw_02_goalkeepers.loc[(gw_02_goalkeepers['pred_02'] >= 12) & (gw_02_goalkeepers['confidence_01'].between(.4, .6)),
                            'INVEST'] = 'YES'

    predicted_gw_02 = pd.DataFrame(columns=['G'])
    gw_02_goalkeepers.sort_values(by=['pred_02'], ascending=False, inplace=True)
    predicted_gw_02['G'] = gw_02_goalkeepers['name'].head(70)

    # STEP 3: List Investment Level Defenders
    gw_02_defenders = predicted_gameweek[predicted_gameweek['position'].str.contains('D', na=False)]
    gw_02_defenders.sort_values(by=['amp_02', 'pred_02'], ascending=False, inplace=True)

    # STEP 4: List Investment Level Midfielders and Forwards:
    gw_02_mids_fwds = predicted_gameweek[predicted_gameweek['position'].str.contains('M|F', na=False)]

    gw_02_mids_fwds['confidence_01'] = 0

    gw_02_mids_fwds.loc[((gw_02_mids_fwds['pred_01'] <= 12) & (gw_02_mids_fwds['gw_01'] <= 12)) |
        ((gw_02_mids_fwds['pred_01'] >= 12) & (gw_02_mids_fwds['gw_01'] >= 12)), 'confidence_01'] = 1

    gw_02_mids_fwds['INVEST'] = 'NO'
    gw_02_mids_fwds.loc[(gw_02_mids_fwds['pred_02'] >= 12) & (gw_02_mids_fwds['confidence_01'] > .4999),
                            'INVEST'] = 'YES'
    mf_invest = gw_02_mids_fwds[gw_02_mids_fwds['INVEST']=='YES']
    mf_invest.sort_values(by=['pred_02'], ascending=False, inplace=True)

    with pd.ExcelWriter('gameweek_02.xlsx') as writer:
        predicted_gw_02['G'].to_excel(writer, sheet_name='GK')
        gw_02_defenders.to_excel(writer, sheet_name='DEF')
        mf_invest['name'].to_excel(writer, sheet_name='MF')

    return predicted_gameweek


def predict_gw_03(predicted_gameweek):
    '''Predicts Gameweek 3
    param: predicted_gameweek'''

    # STEP 1(a): get the % diff between predicted and actual for the prior gameweek
    predicted_gameweek.loc[predicted_gameweek['min_02'] == 0, 'gw_02'] = predicted_gameweek['pred_02']

    predicted_gameweek['diff_02'] = (predicted_gameweek['gw_02'] - predicted_gameweek['pred_02']) / predicted_gameweek[
        'pred_02']
    predicted_gameweek['diff_02'].replace([np.inf, -np.inf], 0, inplace=True)
    predicted_gameweek['diff_02'].clip(upper=1, axis=0, inplace=True)

    # STEP 1(b): Create prediction for second week:
    predicted_gameweek['pred_03'] = ((((predicted_gameweek['gw_01'] - predicted_gameweek['amp_01']) +
                                      (predicted_gameweek['gw_02'] - predicted_gameweek['amp_02'])) / 2)
                                     + predicted_gameweek['amp_03']) * (1 + (predicted_gameweek['diff_01'] / 5)) * \
                                    (1 + (predicted_gameweek['diff_02'] / 5))

    predicted_gameweek = predicted_gameweek[sorted(predicted_gameweek.columns, key=lambda x: x[-2:])]

    # STEP 2: List Investment Level Goalkeepers
    gw_03_goalkeepers = predicted_gameweek[predicted_gameweek['position'] == 'G']

    gw_03_goalkeepers['confidence_01'] = 0
    gw_03_goalkeepers['confidence_02'] = 0

    gw_03_goalkeepers.loc[((gw_03_goalkeepers['pred_01'] <= 12) & (gw_03_goalkeepers['gw_01'] <= 12)) |
        ((gw_03_goalkeepers['pred_01'] >= 12) & (gw_03_goalkeepers['gw_01'] >= 12)), 'confidence_01'] = 1

    gw_03_goalkeepers.loc[((gw_03_goalkeepers['pred_02'] <= 12) & (gw_03_goalkeepers['gw_02'] <= 12)) |
                          ((gw_03_goalkeepers['pred_02'] >= 12) & (
                                      gw_03_goalkeepers['gw_02'] >= 12)), 'confidence_02'] = 1

    gw_03_goalkeepers['avg_confidence'] = gw_03_goalkeepers[['confidence_01', 'confidence_02']].mean(axis=1)

    gw_03_goalkeepers['INVEST'] = 'NO'
    gw_03_goalkeepers.loc[(gw_03_goalkeepers['pred_03'] >= 12) & (gw_03_goalkeepers['avg_confidence'].between(.4, .6)),
                          'INVEST'] = 'YES'

    gk_invest = gw_03_goalkeepers[gw_03_goalkeepers['INVEST'] == 'YES']
    gk_invest.sort_values(by=['pred_03'], ascending=False, inplace=True)

    # STEP 3: List Investment Level Defenders
    gw_03_defenders = predicted_gameweek[predicted_gameweek['position'].str.contains('D', na=False)]
    gw_03_defenders.sort_values(by=['amp_03', 'pred_03'], ascending=False, inplace=True)


    # STEP e: List Investment Level Midfielders and Forwards:
    gw_03_mids_fwds = predicted_gameweek[predicted_gameweek['position'].str.contains('M|F', na=False)]

    gw_03_mids_fwds['confidence_01'] = 0
    gw_03_mids_fwds['confidence_02'] = 0

    gw_03_mids_fwds.loc[((gw_03_mids_fwds['pred_01'] <= 12) & (gw_03_mids_fwds['gw_01'] <= 12)) |
                        ((gw_03_mids_fwds['pred_01'] >= 12) & (gw_03_mids_fwds['gw_01'] >= 12)), 'confidence_01'] = 1
    gw_03_mids_fwds.loc[((gw_03_mids_fwds['pred_02'] <= 12) & (gw_03_mids_fwds['gw_02'] <= 12)) |
                        ((gw_03_mids_fwds['pred_02'] >= 12) & (gw_03_mids_fwds['gw_02'] >= 12)), 'confidence_02'] = 1

    gw_03_mids_fwds['avg_confidence'] = gw_03_mids_fwds[['confidence_01', 'confidence_02']].mean(axis=1)

    gw_03_mids_fwds['INVEST'] = 'NO'
    gw_03_mids_fwds.loc[(gw_03_mids_fwds['pred_03'] >= 12) & (gw_03_mids_fwds['avg_confidence'] > .4999),
                        'INVEST'] = 'YES'
    mf_invest = gw_03_mids_fwds[gw_03_mids_fwds['INVEST'] == 'YES']
    mf_invest.sort_values(by=['pred_03'], ascending=False, inplace=True)

    with pd.ExcelWriter('gameweek_03.xlsx') as writer:
        gk_invest['name'].to_excel(writer, sheet_name='GK')
        gw_03_defenders[['name', 'team']].to_excel(writer, sheet_name='DEF')
        mf_invest['name'].to_excel(writer, sheet_name='MF')

    return predicted_gameweek


def predict_gw_04(predicted_gameweek):
    '''Predicts Gameweek 4
    param: predicted_gameweek'''

    # STEP 1(a): get the % diff between predicted and actual for the prior gameweek
    predicted_gameweek.loc[predicted_gameweek['min_03'] == 0, 'gw_03'] = predicted_gameweek['pred_03']

    predicted_gameweek['diff_03'] = (predicted_gameweek['gw_03'] - predicted_gameweek['pred_03']) / predicted_gameweek[
        'pred_03']
    predicted_gameweek['diff_03'].replace([np.inf, -np.inf], 0, inplace=True)
    predicted_gameweek['diff_03'].clip(upper=1, axis=0, inplace=True)

    # STEP 1(b): Create prediction for second week:
    predicted_gameweek['pred_04'] = ((((predicted_gameweek['gw_01'] - predicted_gameweek['amp_01']) +
                                      (predicted_gameweek['gw_02'] - predicted_gameweek['amp_02']) +
                                       (predicted_gameweek['gw_03'] - predicted_gameweek['amp_03'])) / 3)
                                     + predicted_gameweek['amp_04']) * (1 + (predicted_gameweek['diff_01'] / 5)) * \
                                    (1 + (predicted_gameweek['diff_02'] / 5))*(1 + (predicted_gameweek['diff_03'] / 5))

    predicted_gameweek = predicted_gameweek[sorted(predicted_gameweek.columns, key=lambda x: x[-2:])]

    # STEP 2: List Investment Level Goalkeepers
    gw_04_goalkeepers = predicted_gameweek[predicted_gameweek['position'] == 'G']

    gw_04_goalkeepers['confidence_01'] = 0
    gw_04_goalkeepers['confidence_02'] = 0
    gw_04_goalkeepers['confidence_03'] = 0

    gw_04_goalkeepers.loc[((gw_04_goalkeepers['pred_01'] <= 12) & (gw_04_goalkeepers['gw_01'] <= 12)) |
        ((gw_04_goalkeepers['pred_01'] >= 12) & (gw_04_goalkeepers['gw_01'] >= 12)), 'confidence_01'] = 1

    gw_04_goalkeepers.loc[((gw_04_goalkeepers['pred_02'] <= 12) & (gw_04_goalkeepers['gw_02'] <= 12)) |
                          ((gw_04_goalkeepers['pred_02'] >= 12) & (
                                      gw_04_goalkeepers['gw_02'] >= 12)), 'confidence_02'] = 1

    gw_04_goalkeepers.loc[((gw_04_goalkeepers['pred_03'] <= 12) & (gw_04_goalkeepers['gw_03'] <= 12)) |
        ((gw_04_goalkeepers['pred_03'] >= 12) & (gw_04_goalkeepers['gw_03'] >= 12)), 'confidence_03'] = 1

    gw_04_goalkeepers['avg_confidence'] = gw_04_goalkeepers[['confidence_01', 'confidence_02', 'confidence_03']]\
        .mean(axis=1)

    gw_04_goalkeepers['INVEST'] = 'NO'
    gw_04_goalkeepers.sort_values(by=['pred_04'], ascending=False, inplace=True)
    gw_04_goalkeepers.loc[(gw_04_goalkeepers['pred_04'] >= 12) & (gw_04_goalkeepers['avg_confidence'].between(.4, .6)),
                          'INVEST'] = 'YES'

    gk_invest = gw_04_goalkeepers[gw_04_goalkeepers['INVEST'] == 'YES']
    gk_invest.sort_values(by=['pred_04'], ascending=False, inplace=True)


    # STEP 3: List Investment Level Defenders
    gw_04_defenders = predicted_gameweek[predicted_gameweek['position'].str.contains('D', na=False)]
    gw_04_defenders.sort_values(by=['amp_04', 'pred_04'], ascending=False, inplace=True)

    # STEP 4: List Investment Level Midfielders and Forwards:
    gw_04_mids_fwds = predicted_gameweek[predicted_gameweek['position'].str.contains('M|F', na=False)]

    gw_04_mids_fwds['confidence_01'] = 0
    gw_04_mids_fwds['confidence_02'] = 0
    gw_04_mids_fwds['confidence_03'] = 0

    gw_04_mids_fwds.loc[((gw_04_mids_fwds['pred_01'] <= 12) & (gw_04_mids_fwds['gw_01'] <= 12)) |
                        ((gw_04_mids_fwds['pred_01'] >= 12) & (gw_04_mids_fwds['gw_01'] >= 12)), 'confidence_01'] = 1
    gw_04_mids_fwds.loc[((gw_04_mids_fwds['pred_02'] <= 12) & (gw_04_mids_fwds['gw_02'] <= 12)) |
                        ((gw_04_mids_fwds['pred_02'] >= 12) & (gw_04_mids_fwds['gw_02'] >= 12)), 'confidence_02'] = 1
    gw_04_mids_fwds.loc[((gw_04_mids_fwds['pred_03'] <= 12) & (gw_04_mids_fwds['gw_03'] <= 12)) |
                        ((gw_04_mids_fwds['pred_03'] >= 12) & (gw_04_mids_fwds['gw_03'] >= 12)), 'confidence_03'] = 1

    gw_04_mids_fwds['avg_confidence'] = gw_04_mids_fwds[['confidence_01', 'confidence_02', 'confidence_03']].mean(axis=1)

    gw_04_mids_fwds['INVEST'] = 'NO'
    gw_04_mids_fwds.loc[(gw_04_mids_fwds['pred_04'] >= 12) & (gw_04_mids_fwds['avg_confidence'] > .4999),
                        'INVEST'] = 'YES'
    mf_invest = gw_04_mids_fwds[gw_04_mids_fwds['INVEST'] == 'YES']
    mf_invest.sort_values(by=['pred_04'], ascending=False, inplace=True)

    with pd.ExcelWriter('gameweek_04.xlsx') as writer:
        gw_04_goalkeepers['name'].to_excel(writer, sheet_name='GK')
        gw_04_defenders[['name', 'team']].to_excel(writer, sheet_name='DEF')
        mf_invest['name'].to_excel(writer, sheet_name='MF')

    return predicted_gameweek


def predict_gw_05(predicted_gameweek):
    '''Predicts Gameweek 5
    param: predicted_gameweek'''

    # STEP 1(a): get the % diff between predicted and actual for the prior gameweek
    predicted_gameweek.loc[predicted_gameweek['min_04'] == 0, 'gw_04'] = predicted_gameweek['pred_04']

    predicted_gameweek['diff_04'] = (predicted_gameweek['gw_04'] - predicted_gameweek['pred_04']) / predicted_gameweek[
        'pred_04']
    predicted_gameweek['diff_04'].replace([np.inf, -np.inf], 0, inplace=True)
    predicted_gameweek['diff_04'].clip(upper=1, axis=0, inplace=True)

    # STEP 1(b): Create prediction for second week:
    predicted_gameweek['pred_05'] = ((((predicted_gameweek['gw_01'] - predicted_gameweek['amp_01']) +
                                       (predicted_gameweek['gw_02'] - predicted_gameweek['amp_02']) +
                                       (predicted_gameweek['gw_03'] - predicted_gameweek['amp_03']) +
                                      (predicted_gameweek['gw_04'] - predicted_gameweek['amp_04']))/ 4)
                                     + predicted_gameweek['amp_05']) * (1 + (predicted_gameweek['diff_01'] / 5)) * \
                                    (1 + (predicted_gameweek['diff_02'] / 5)) * (1 + (predicted_gameweek['diff_03'] / 5))\
                                                     * (1 + (predicted_gameweek['diff_04'] / 5))

    predicted_gameweek = predicted_gameweek[sorted(predicted_gameweek.columns, key=lambda x: x[-2:])]

    # STEP 2: List Investment Level Goalkeepers
    gw_05_goalkeepers = predicted_gameweek[predicted_gameweek['position'] == 'G']

    gw_05_goalkeepers['confidence_01'] = 0
    gw_05_goalkeepers['confidence_02'] = 0
    gw_05_goalkeepers['confidence_03'] = 0
    gw_05_goalkeepers['confidence_04'] = 0

    gw_05_goalkeepers.loc[((gw_05_goalkeepers['pred_01'] <= 12) & (gw_05_goalkeepers['gw_01'] <= 12)) |
                          ((gw_05_goalkeepers['pred_01'] >= 12) & (
                                      gw_05_goalkeepers['gw_01'] >= 12)), 'confidence_01'] = 1

    gw_05_goalkeepers.loc[((gw_05_goalkeepers['pred_02'] <= 12) & (gw_05_goalkeepers['gw_02'] <= 12)) |
                          ((gw_05_goalkeepers['pred_02'] >= 12) & (
                                  gw_05_goalkeepers['gw_02'] >= 12)), 'confidence_02'] = 1

    gw_05_goalkeepers.loc[((gw_05_goalkeepers['pred_03'] <= 12) & (gw_05_goalkeepers['gw_03'] <= 12)) |
                          ((gw_05_goalkeepers['pred_03'] >= 12) & (
                                      gw_05_goalkeepers['gw_03'] >= 12)), 'confidence_03'] = 1

    gw_05_goalkeepers.loc[((gw_05_goalkeepers['pred_04'] <= 12) & (gw_05_goalkeepers['gw_04'] <= 12)) |
                          ((gw_05_goalkeepers['pred_04'] >= 12) & (
                                      gw_05_goalkeepers['gw_04'] >= 12)), 'confidence_04'] = 1

    gw_05_goalkeepers['avg_confidence'] = gw_05_goalkeepers[['confidence_01', 'confidence_02',
                                                             'confidence_03', 'confidence_04']] \
        .mean(axis=1)

    gw_05_goalkeepers['INVEST'] = 'NO'
    gw_05_goalkeepers.sort_values(by=['pred_05'], ascending=False, inplace=True)
    gw_05_goalkeepers.loc[(gw_05_goalkeepers['pred_05'] >= 12) & (gw_05_goalkeepers['avg_confidence'].between(.4, .6)),
                          'INVEST'] = 'YES'

    gk_invest = gw_05_goalkeepers[gw_05_goalkeepers['INVEST'] == 'YES']
    gk_invest.sort_values(by=['pred_05'], ascending=False, inplace=True)

    # STEP 3: List Investment Level Defenders
    gw_05_defenders = predicted_gameweek[predicted_gameweek['position'].str.contains('D', na=False)]
    gw_05_defenders.sort_values(by=['amp_05', 'pred_05'], ascending=False, inplace=True)

    # STEP 4: List Investment Level Midfielders and Forwards:
    gw_05_mids_fwds = predicted_gameweek[predicted_gameweek['position'].str.contains('M|F', na=False)]

    gw_05_mids_fwds['confidence_01'] = 0
    gw_05_mids_fwds['confidence_02'] = 0
    gw_05_mids_fwds['confidence_03'] = 0
    gw_05_mids_fwds['confidence_04'] = 0

    gw_05_mids_fwds.loc[((gw_05_mids_fwds['pred_01'] <= 12) & (gw_05_mids_fwds['gw_01'] <= 12)) |
                        ((gw_05_mids_fwds['pred_01'] >= 12) & (gw_05_mids_fwds['gw_01'] >= 12)), 'confidence_01'] = 1
    gw_05_mids_fwds.loc[((gw_05_mids_fwds['pred_02'] <= 12) & (gw_05_mids_fwds['gw_02'] <= 12)) |
                        ((gw_05_mids_fwds['pred_02'] >= 12) & (gw_05_mids_fwds['gw_02'] >= 12)), 'confidence_02'] = 1
    gw_05_mids_fwds.loc[((gw_05_mids_fwds['pred_03'] <= 12) & (gw_05_mids_fwds['gw_03'] <= 12)) |
                        ((gw_05_mids_fwds['pred_03'] >= 12) & (gw_05_mids_fwds['gw_03'] >= 12)), 'confidence_03'] = 1
    gw_05_mids_fwds.loc[((gw_05_mids_fwds['pred_04'] <= 12) & (gw_05_mids_fwds['gw_04'] <= 12)) |
                        ((gw_05_mids_fwds['pred_04'] >= 12) & (gw_05_mids_fwds['gw_04'] >= 12)), 'confidence_04'] = 1

    gw_05_mids_fwds['avg_confidence'] = gw_05_mids_fwds[['confidence_01', 'confidence_02',
                                                         'confidence_03', 'confidence_04']].mean(
        axis=1)

    gw_05_mids_fwds['INVEST'] = 'NO'
    gw_05_mids_fwds.loc[(gw_05_mids_fwds['pred_05'] >= 12) & (gw_05_mids_fwds['avg_confidence'] > .4999),
                        'INVEST'] = 'YES'
    mf_invest = gw_05_mids_fwds[gw_05_mids_fwds['INVEST'] == 'YES']
    mf_invest.sort_values(by=['pred_05'], ascending=False, inplace=True)

    with pd.ExcelWriter('gameweek_05.xlsx') as writer:
        gk_invest[['name', 'pred_05']].to_excel(writer, sheet_name='GK')
        gw_05_defenders[['name', 'team']].to_excel(writer, sheet_name='DEF')
        mf_invest[['name', 'pred_05']].to_excel(writer, sheet_name='MF')

    return predicted_gameweek


def predict_gw_06_09(predicted_gameweek, gw_int):
    '''Predicts Gameweek 6 to 9
    param: predicted_gameweek'''

    # STEP 1(a): get the % diff between predicted and actual for the prior gameweek
    predicted_gameweek.loc[predicted_gameweek['min_0{}'.format(str(gw_int-1))] == 0, 'gw_0{}'.format(str(gw_int-1))]\
        = predicted_gameweek['pred_0{}'.format(str(gw_int-1))]

    predicted_gameweek['diff_0{}'.format(str(gw_int-1))] = (predicted_gameweek['gw_0{}'.format(str(gw_int-1))] -
                                                            predicted_gameweek['pred_0{}'.format(str(gw_int-1))]) / \
                                                            predicted_gameweek['pred_0{}'.format(str(gw_int-1))]
    predicted_gameweek['diff_0{}'.format(str(gw_int-1))].replace([np.inf, -np.inf], 0, inplace=True)
    predicted_gameweek['diff_0{}'.format(str(gw_int-1))].clip(upper=1, axis=0, inplace=True)

    # STEP 1(b): Create prediction for second week:
    predicted_gameweek['pred_0{}'.format(str(gw_int))] = \
        ((((predicted_gameweek['gw_0{}'.format(str(gw_int-5))] - predicted_gameweek['amp_0{}'.format(str(gw_int-5))]) +
           (predicted_gameweek['gw_0{}'.format(str(gw_int-4))] - predicted_gameweek['amp_0{}'.format(str(gw_int-4))]) +
           (predicted_gameweek['gw_0{}'.format(str(gw_int-3))] - predicted_gameweek['amp_0{}'.format(str(gw_int-3))]) +
           (predicted_gameweek['gw_0{}'.format(str(gw_int-2))] - predicted_gameweek['amp_0{}'.format(str(gw_int-2))]) +
           (predicted_gameweek['gw_0{}'.format(str(gw_int-1))] - predicted_gameweek['amp_0{}'.format(str(gw_int-1))]))
          / 5) + predicted_gameweek['amp_0{}'.format(str(gw_int))])\
                                     * (1 + (predicted_gameweek['diff_0{}'.format(str(gw_int-5))] / 5))\
                                     * (1 + (predicted_gameweek['diff_0{}'.format(str(gw_int-4))] / 5))\
                                     * (1 + (predicted_gameweek['diff_0{}'.format(str(gw_int-3))] / 5))\
                                     * (1 + (predicted_gameweek['diff_0{}'.format(str(gw_int-2))] / 5))\
                                     * (1 + (predicted_gameweek['diff_0{}'.format(str(gw_int-1))] / 5))

    predicted_gameweek = predicted_gameweek[sorted(predicted_gameweek.columns, key=lambda x: x[-2:])]

    # STEP 2: List Investment Level Goalkeepers
    goalkeepers = predicted_gameweek[predicted_gameweek['position'] == 'G']

    goalkeepers['confidence_0{}'.format(str(gw_int-5))] = 0
    goalkeepers['confidence_0{}'.format(str(gw_int-4))] = 0
    goalkeepers['confidence_0{}'.format(str(gw_int-3))] = 0
    goalkeepers['confidence_0{}'.format(str(gw_int-2))] = 0
    goalkeepers['confidence_0{}'.format(str(gw_int-1))] = 0

    for i in np.arange(5, 0, -1):
        goalkeepers.loc[((goalkeepers['pred_0{}'.format(str(gw_int-i))] <= 12) &
                         (goalkeepers['gw_0{}'.format(str(gw_int-i))] <= 12)) |
                        ((goalkeepers['pred_0{}'.format(str(gw_int-i))] >= 12) & (
                       goalkeepers['gw_0{}'.format(str(gw_int-i))] >= 12)), 'confidence_0{}'.format(str(gw_int-i))] = 1

    goalkeepers['avg_confidence'] = goalkeepers[['confidence_0{}'.format(str(gw_int-5)),
                                                 'confidence_0{}'.format(str(gw_int-4)),
                                                 'confidence_0{}'.format(str(gw_int-3)),
                                                 'confidence_0{}'.format(str(gw_int-2)),
                                                 'confidence_0{}'.format(str(gw_int-1))]].mean(axis=1)

    goalkeepers['INVEST'] = 'NO'
    goalkeepers.sort_values(by=['pred_0{}'.format(str(gw_int))], ascending=False, inplace=True)
    goalkeepers.loc[(goalkeepers['pred_0{}'.format(str(gw_int))] >= 12) & (goalkeepers['avg_confidence'].between(.4, .6)),
                          'INVEST'] = 'YES'

    gk_invest = goalkeepers[goalkeepers['INVEST'] == 'YES']
    gk_invest.sort_values(by=['pred_0{}'.format(str(gw_int))], ascending=False, inplace=True)

    # STEP 3: List Investment Level Defenders
    defenders = predicted_gameweek[predicted_gameweek['position'].str.contains('D', na=False)]
    defenders.sort_values(by=['amp_0{}'.format(str(gw_int)),
                                    'pred_0{}'.format(str(gw_int))], ascending=False, inplace=True)

    # STEP 4: List Investment Level Midfielders and Forwards:
    mids_fwds = predicted_gameweek[predicted_gameweek['position'].str.contains('M|F', na=False)]

    mids_fwds['confidence_0{}'.format(str(gw_int-5))] = 0
    mids_fwds['confidence_0{}'.format(str(gw_int-4))] = 0
    mids_fwds['confidence_0{}'.format(str(gw_int-3))] = 0
    mids_fwds['confidence_0{}'.format(str(gw_int-2))] = 0
    mids_fwds['confidence_0{}'.format(str(gw_int-1))] = 0

    for i in np.arange(5, 0, -1):
        mids_fwds.loc[((mids_fwds['pred_0{}'.format(str(gw_int-i))] <= 12) &
                         (mids_fwds['gw_0{}'.format(str(gw_int-i))] <= 12)) |
                        ((mids_fwds['pred_0{}'.format(str(gw_int-i))] >= 12) & (
                       mids_fwds['gw_0{}'.format(str(gw_int-i))] >= 12)), 'confidence_0{}'.format(str(gw_int-i))] = 1

    mids_fwds['avg_confidence'] = mids_fwds[['confidence_0{}'.format(str(gw_int-5)),
                                               'confidence_0{}'.format(str(gw_int-4)),
                                             'confidence_0{}'.format(str(gw_int-3)),
                                             'confidence_0{}'.format(str(gw_int-2)),
                                             'confidence_0{}'.format(str(gw_int-1))]].mean(axis=1)

    mids_fwds['INVEST'] = 'NO'
    mids_fwds.loc[(mids_fwds['pred_0{}'.format(str(gw_int))] >= 12) & (mids_fwds['avg_confidence'] > .4999),
                        'INVEST'] = 'YES'
    mf_invest = mids_fwds[mids_fwds['INVEST'] == 'YES']

    eighty_eight_single = call_single_88(1, gw_int-1, 8)
    aggregates = agg_single_gw(eighty_eight_single[0], eighty_eight_single[1],
                               eighty_eight_single[2], eighty_eight_single[3])

    mf_invest = pd.merge(mf_invest, aggregates, how='left', on='name')
    mf_invest.sort_values(by=['Total'.format(str(gw_int))], ascending=False, inplace=True)

    with pd.ExcelWriter('gameweek_0{}.xlsx'.format(str(gw_int))) as writer:
        gk_invest[['name', 'pred_0{}'.format(str(gw_int))]].to_excel(writer, sheet_name='GK')
        defenders[['name', 'team']].to_excel(writer, sheet_name='DEF')
        mf_invest[['name', 'pred_0{}'.format(str(gw_int))]].to_excel(writer, sheet_name='MF')

    return predicted_gameweek


def predict_gw_10_plus(predicted_gameweek, gw_int):
    '''Predicts Gameweek 6 to 9
    param: predicted_gameweek'''

    str(gw_int)

    # STEP 1(a): get the % diff between predicted and actual for the prior gameweek
    predicted_gameweek.loc[predicted_gameweek['min_{}'.format(str(gw_int-1).zfill(2))] == 0, 'gw_{}'.format(str(gw_int-1).zfill(2))]\
        = predicted_gameweek['pred_{}'.format(str(gw_int-1).zfill(2))]

    predicted_gameweek['diff_{}'.format(str(gw_int-1).zfill(2))] = (predicted_gameweek['gw_{}'.format(str(gw_int-1).zfill(2))] -
                                                            predicted_gameweek['pred_{}'.format(str(gw_int-1).zfill(2))]) / \
                                                            predicted_gameweek['pred_{}'.format(str(gw_int-1).zfill(2))]
    predicted_gameweek['diff_{}'.format(str(gw_int-1).zfill(2))].replace([np.inf, -np.inf], 0, inplace=True)
    predicted_gameweek['diff_{}'.format(str(gw_int-1).zfill(2))].clip(upper=1, axis=0, inplace=True)

    # STEP 1(b): Create prediction for second week:
    predicted_gameweek['pred_{}'.format(str(gw_int).zfill(2))] = \
        ((((predicted_gameweek['gw_{}'.format(str(gw_int-5).zfill(2))] - predicted_gameweek['amp_{}'.format(str(gw_int-5).zfill(2))]) +
           (predicted_gameweek['gw_{}'.format(str(gw_int-4).zfill(2))] - predicted_gameweek['amp_{}'.format(str(gw_int-4).zfill(2))]) +
           (predicted_gameweek['gw_{}'.format(str(gw_int-3).zfill(2))] - predicted_gameweek['amp_{}'.format(str(gw_int-3).zfill(2))]) +
           (predicted_gameweek['gw_{}'.format(str(gw_int-2).zfill(2))] - predicted_gameweek['amp_{}'.format(str(gw_int-2).zfill(2))]) +
           (predicted_gameweek['gw_{}'.format(str(gw_int-1).zfill(2))] - predicted_gameweek['amp_{}'.format(str(gw_int-1).zfill(2))]))
          / 5) + predicted_gameweek['amp_{}'.format(str(gw_int).zfill(2))])\
                                     * (1 + (predicted_gameweek['diff_{}'.format(str(gw_int-5).zfill(2))] / 5))\
                                     * (1 + (predicted_gameweek['diff_{}'.format(str(gw_int-4).zfill(2))] / 5))\
                                     * (1 + (predicted_gameweek['diff_{}'.format(str(gw_int-3).zfill(2))] / 5))\
                                     * (1 + (predicted_gameweek['diff_{}'.format(str(gw_int-2).zfill(2))] / 5))\
                                     * (1 + (predicted_gameweek['diff_{}'.format(str(gw_int-1).zfill(2))] / 5))

    predicted_gameweek = predicted_gameweek[sorted(predicted_gameweek.columns, key=lambda x: x[-2:])]

    # STEP 2: List Investment Level Goalkeepers
    goalkeepers = predicted_gameweek[predicted_gameweek['position'] == 'G']

    goalkeepers['confidence_{}'.format(str(gw_int-5).zfill(2))] = 0
    goalkeepers['confidence_{}'.format(str(gw_int-4).zfill(2))] = 0
    goalkeepers['confidence_{}'.format(str(gw_int-3).zfill(2))] = 0
    goalkeepers['confidence_{}'.format(str(gw_int-2).zfill(2))] = 0
    goalkeepers['confidence_{}'.format(str(gw_int-1).zfill(2))] = 0

    for i in np.arange(5, 0, -1):
        goalkeepers.loc[((goalkeepers['pred_{}'.format(str(gw_int-i).zfill(2))] <= 12) &
                         (goalkeepers['gw_{}'.format(str(gw_int-i).zfill(2))] <= 12)) |
                        ((goalkeepers['pred_{}'.format(str(gw_int-i).zfill(2))] >= 12) & (
                       goalkeepers['gw_{}'.format(str(gw_int-i).zfill(2))] >= 12)), 'confidence_{}'.format(str(gw_int-i).zfill(2))] = 1

    goalkeepers['avg_confidence'] = goalkeepers[['confidence_{}'.format(str(gw_int-5).zfill(2)),
                                                 'confidence_{}'.format(str(gw_int-4).zfill(2)),
                                                 'confidence_{}'.format(str(gw_int-3).zfill(2)),
                                                 'confidence_{}'.format(str(gw_int-2).zfill(2)),
                                                 'confidence_{}'.format(str(gw_int-1).zfill(2))]].mean(axis=1)

    goalkeepers['INVEST'] = 'NO'
    goalkeepers.sort_values(by=['pred_{}'.format(str(gw_int))], ascending=False, inplace=True)
    goalkeepers.loc[(goalkeepers['pred_{}'.format(str(gw_int))] >= 12) & (goalkeepers['avg_confidence'].between(.4, .6)),
                          'INVEST'] = 'YES'

    gk_invest = goalkeepers[goalkeepers['INVEST'] == 'YES']
    gk_invest.sort_values(by=['pred_{}'.format(str(gw_int))], ascending=False, inplace=True)

    # STEP 3: List Investment Level Defenders
    defenders = predicted_gameweek[predicted_gameweek['position'].str.contains('D', na=False)]
    defenders.sort_values(by=['amp_{}'.format(str(gw_int)),
                                    'pred_{}'.format(str(gw_int))], ascending=False, inplace=True)

    # STEP 4: List Investment Level Midfielders and Forwards:
    mids_fwds = predicted_gameweek[predicted_gameweek['position'].str.contains('M|F', na=False)]

    mids_fwds['confidence_{}'.format(str(gw_int-5).zfill(2))] = 0
    mids_fwds['confidence_{}'.format(str(gw_int-4).zfill(2))] = 0
    mids_fwds['confidence_{}'.format(str(gw_int-3).zfill(2))] = 0
    mids_fwds['confidence_{}'.format(str(gw_int-2).zfill(2))] = 0
    mids_fwds['confidence_{}'.format(str(gw_int-1).zfill(2))] = 0

    for i in np.arange(5, 0, -1):
        mids_fwds.loc[((mids_fwds['pred_{}'.format(str(gw_int-i).zfill(2))] <= 12) &
                         (mids_fwds['gw_{}'.format(str(gw_int-i).zfill(2))] <= 12)) |
                        ((mids_fwds['pred_{}'.format(str(gw_int-i).zfill(2))] >= 12) & (
                       mids_fwds['gw_{}'.format(str(gw_int-i).zfill(2))] >= 12)), 'confidence_{}'.format(str(gw_int-i).zfill(2))] = 1

    mids_fwds['avg_confidence'] = mids_fwds[['confidence_{}'.format(str(gw_int-5).zfill(2)),
                                             'confidence_{}'.format(str(gw_int-4).zfill(2)),
                                             'confidence_{}'.format(str(gw_int-3).zfill(2)),
                                             'confidence_{}'.format(str(gw_int-2).zfill(2)),
                                             'confidence_{}'.format(str(gw_int-1).zfill(2))]].mean(axis=1)

    mids_fwds['INVEST'] = 'NO'
    mids_fwds.loc[(mids_fwds['pred_{}'.format(str(gw_int))] >= 12) & (mids_fwds['avg_confidence'] > .4999),
                        'INVEST'] = 'YES'
    mf_invest = mids_fwds[mids_fwds['INVEST'] == 'YES']

    eighty_eight_single = call_single_88(1, gw_int-1, 8)
    aggregates = agg_single_gw(eighty_eight_single[0], eighty_eight_single[1],
                               eighty_eight_single[2], eighty_eight_single[3])

    mf_invest = pd.merge(mf_invest, aggregates, how='left', on='name')
    mf_invest.sort_values(by=['Total'.format(str(gw_int))], ascending=False, inplace=True)

    with pd.ExcelWriter('gameweek_{}.xlsx'.format(str(gw_int))) as writer:
        gk_invest[['name', 'pred_{}'.format(str(gw_int))]].to_excel(writer, sheet_name='GK')
        defenders[['name', 'team']].to_excel(writer, sheet_name='DEF')
        mf_invest[['name', 'pred_{}'.format(str(gw_int))]].to_excel(writer, sheet_name='MF')

    return predicted_gameweek
