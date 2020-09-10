import pandas as pd
import numpy as np

def best16_gk(df):
    gk_df = df[df['Position'] == 'G']
    gk_df = gk_df.sort_values(by='FPts', ascending=False)
    return gk_df[:16]


def best16_def(df):
    def_df = df[df['Position'].str.contains("D")]
    def_df = def_df.sort_values(by='FPts', ascending=False)
    return def_df[:64]


def best16_mid(df):
    mid_df = df[df['Position'].str.contains("M")]
    mid_df = mid_df.sort_values(by='FPts', ascending=False)
    return mid_df[:64]


def best16_fwd(df):
    fwd_df = df[df['Position'].str.contains("F")]
    fwd_df = fwd_df.sort_values(by='FPts', ascending=False)
    return fwd_df[:32]


def team_creator(gameweek, team_nos):
    teams = pd.DataFrame()
    for i in team_nos:
        goalkeepers = best16_gk(gameweek)
        defenders = best16_def(gameweek)
        midfielders = best16_mid(gameweek)
        forwards = best16_fwd(gameweek)

        team_01 = pd.DataFrame(columns=['Team', 'Pos', 'Pts'])
        team_01 = team_01.append({'Team': goalkeepers.iloc[0, 0], 'Pos': goalkeepers.iloc[0, 2],
                                  'Pts': goalkeepers.iloc[0, 6]}, ignore_index=True)
        team_01 = team_01.append({'Team': defenders.iloc[0, 0], 'Pos': defenders.iloc[0, 2],
                                  'Pts': defenders.iloc[0, 6]}, ignore_index=True)
        team_01 = team_01.append({'Team': defenders.iloc[1, 0], 'Pos': defenders.iloc[1, 2],
                                  'Pts': defenders.iloc[1, 6]}, ignore_index=True)
        team_01 = team_01.append({'Team': defenders.iloc[2, 0], 'Pos': defenders.iloc[2, 2],
                                  'Pts': defenders.iloc[2, 6]}, ignore_index=True)
        team_01 = team_01.append({'Team': midfielders.iloc[0, 0], 'Pos': midfielders.iloc[0, 2],
                                  'Pts': midfielders.iloc[0, 6]}, ignore_index=True)
        team_01 = team_01.append({'Team': midfielders.iloc[1, 0], 'Pos': midfielders.iloc[1, 2],
                                  'Pts': midfielders.iloc[1, 6]}, ignore_index=True)
        team_01 = team_01.append({'Team': midfielders.iloc[2, 0], 'Pos': midfielders.iloc[2, 2],
                                  'Pts': midfielders.iloc[2, 6]}, ignore_index=True)
        team_01 = team_01.append({'Team': forwards.iloc[0, 0], 'Pos': forwards.iloc[0, 2],
                                  'Pts': forwards.iloc[0, 6]}, ignore_index=True)
        team_01 = team_01.drop_duplicates()

        defenders = defenders.iloc[3:, :]
        midfielders = midfielders.iloc[3:, :]
        forwards = forwards.iloc[1:, :]

        remainder = pd.concat([defenders, midfielders, forwards], ignore_index=True)
        remainder = remainder.sort_values(by='FPts', ascending=False)
        remainder = remainder[~remainder['Player'].isin(team_01['Team'])]
        remainder = remainder.drop_duplicates(keep='first')

        team_01 = team_01.append({'Team': remainder.iloc[0, 0], 'Pos': remainder.iloc[0, 2],
                                  'Pts': remainder.iloc[0, 6]}, ignore_index=True)
        remainder = remainder[~remainder['Player'].isin(team_01['Team'])]
        team_01 = team_01.append({'Team': remainder.iloc[0, 0], 'Pos': remainder.iloc[0, 2],
                                  'Pts': remainder.iloc[0, 6]}, ignore_index=True)
        team_01 = team_01.drop_duplicates()

        # Check1: Have we reached maximum forwards?
        defender_must = team_01['Pos'][team_01['Pos'] == 'D'].count()
        midfielder_must = team_01['Pos'][team_01['Pos'] == 'M'].count()
        forward_must = team_01['Pos'][team_01['Pos'] == 'F'].count()

        if forward_must == 3:
            remainder = remainder[remainder['Position'] != 'F']
        if midfielder_must == 5:
            remainder = remainder[remainder['Position'] != 'M']
        if defender_must == 5:
            remainder = remainder[remainder['Position'] != 'D']
        if len(team_01.index) == 9:
            remainder = remainder[~remainder['Player'].isin(team_01['Team'])]
            team_01 = team_01.append({'Team': remainder.iloc[0,  0], 'Pos': remainder.iloc[0, 2],
                                      'Pts': remainder.iloc[0, 6]}, ignore_index=True)
        if len(team_01.index) == 8:
            remainder = remainder[~remainder['Player'].isin(team_01['Team'])]
            team_01 = team_01.append({'Team': remainder.iloc[0,  0], 'Pos': remainder.iloc[0, 2],
                                      'Pts': remainder.iloc[0, 6]}, ignore_index=True)
            remainder = remainder[~remainder['Player'].isin(team_01['Team'])]
            team_01 = team_01.append({'Team': remainder.iloc[0, 0], 'Pos': remainder.iloc[0, 2],
                                      'Pts': remainder.iloc[0, 6]}, ignore_index=True)

        remainder = remainder[~remainder['Player'].isin(team_01['Team'])]
        team_01 = team_01.append({'Team': remainder.iloc[0, 0], 'Pos': remainder.iloc[0, 2],
                                  'Pts': remainder.iloc[0, 6]}, ignore_index=True)
        teams[i] = team_01['Team']
        gameweek = gameweek[~gameweek['Player'].isin(team_01['Team'])]

    return teams


def call_gameweeks(first_gameweek, last_gameweek):
    # read in raw csv files:
    placeholder_dir = "/Users/johnhughes/fantrax_django/score_predictor/core/fixtures/gameweeks/"

    # TODO: This read_csv should be replaced with a more agile approach to facilitate new gameweeks
    GW_01 = pd.read_csv(placeholder_dir + "GW_01.csv")
    GW_02 = pd.read_csv(placeholder_dir + "GW_02.csv")
    GW_03 = pd.read_csv(placeholder_dir + "GW_03.csv")
    GW_04 = pd.read_csv(placeholder_dir + "GW_04.csv")
    GW_05 = pd.read_csv(placeholder_dir + "GW_05.csv")
    GW_06 = pd.read_csv(placeholder_dir + "GW_06.csv")
    GW_07 = pd.read_csv(placeholder_dir + "GW_07.csv")
    GW_08 = pd.read_csv(placeholder_dir + "GW_08.csv")
    GW_09 = pd.read_csv(placeholder_dir + "GW_09.csv")
    GW_10 = pd.read_csv(placeholder_dir + "GW_10.csv")
    GW_11 = pd.read_csv(placeholder_dir + "GW_11.csv")
    GW_12 = pd.read_csv(placeholder_dir + "GW_12.csv")
    GW_13 = pd.read_csv(placeholder_dir + "GW_13.csv")
    GW_14 = pd.read_csv(placeholder_dir + "GW_14.csv")
    GW_15 = pd.read_csv(placeholder_dir + "GW_15.csv")
    GW_16 = pd.read_csv(placeholder_dir + "GW_16.csv")
    GW_17 = pd.read_csv(placeholder_dir + "GW_17.csv")
    GW_18 = pd.read_csv(placeholder_dir + "GW_18.csv")
    GW_19 = pd.read_csv(placeholder_dir + "GW_19.csv")
    GW_20 = pd.read_csv(placeholder_dir + "GW_20.csv")
    GW_21 = pd.read_csv(placeholder_dir + "GW_21.csv")
    GW_22 = pd.read_csv(placeholder_dir + "GW_22.csv")
    GW_23 = pd.read_csv(placeholder_dir + "GW_23.csv")
    GW_24 = pd.read_csv(placeholder_dir + "GW_24.csv")
    GW_25 = pd.read_csv(placeholder_dir + "GW_25.csv")

    # store files in labelled dictionary
    gameweeks = {'GW_01': GW_01, 'GW_02': GW_02, 'GW_03': GW_03, 'GW_04': GW_04, 'GW_05': GW_05, 'GW_06': GW_06,
                 'GW_07': GW_07, 'GW_08': GW_08, 'GW_09': GW_09, 'GW_10': GW_10, 'GW_11': GW_11, 'GW_12': GW_12,
                 'GW_13': GW_13, 'GW_14': GW_14, 'GW_15': GW_15, 'GW_16': GW_16, 'GW_17': GW_17, 'GW_18': GW_18,
                 'GW_19': GW_19, 'GW_20': GW_20, 'GW_21': GW_21, 'GW_22': GW_22, 'GW_23': GW_23, 'GW_24': GW_24,
                 'GW_25': GW_25}

    # dictionary to align gameweek string with input integers. Integers set to string as they are keys.
    gw_to_ints = {'1': 'GW_01', '2':'GW_02', '3':'GW_03', '4':'GW_04', '5':'GW_05', '6':'GW_06',
                 '7':'GW_07', '8':'GW_08', '9':'GW_09', '10':'GW_10', '11':'GW_11', '12':'GW_12',
                 '13':'GW_13', '14':'GW_14', '15':'GW_15', '16':'GW_16', '17':'GW_17', '18':'GW_18',
                 '19':'GW_19', '20':'GW_20', '21':'GW_21', '22':'GW_22', '23':'GW_23', '24':'GW_24',
                 '25':'GW_25'}

    # Create list of integers from input. Convert to string to align with above dictionary keys.
    wanted_gameweeks = np.arange(first_gameweek, last_gameweek+1, 1)
    wanted_gameweeks = [str(element) for element in wanted_gameweeks]

    # Populate my_keys: A list of keys in gameweeks we want the gameweek data.
    my_keys = []
    for key, value in gw_to_ints.items():
        if key in wanted_gameweeks:
            my_keys.append(value)

    #
    chosen_gameweeks = {my_key: gameweeks[my_key] for my_key in my_keys}

    return chosen_gameweeks
