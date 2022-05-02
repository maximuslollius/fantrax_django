import pandas as pd
import numpy as np

latest_gameweek = 1

sheet_names = ['ars', 'avl', 'brf', 'bha', 'bur', 'che', 'cry', 'eve', 'lee', 'lei', 'liv', 'mci', 'mun', 'new', 'nor',
         'sou', 'tot', 'wat', 'whu', 'wol']

complete_norms = pd.DataFrame(columns=['Name', 'Pos', 'Pos ID', 'Date', 'Team', 'Opp', 'Result', 'FPts', 'Min', 'Start',
                                       'Club Idx', 'GW', 'NormScore', 'Prior AVG', 'Predict', 'Return', 'Post AVG',
                                       'CumReturn'])

for sheet_name in sheet_names:
    capitalised_clubname = sheet_name.upper()
    club_df = pd.read_excel(open('FantraxXIs2021_22.xlsx', 'rb'), sheet_name=sheet_name, skiprows=5)
    club_df.drop(['Unnamed: 0', 'Unnamed: 1'], axis=1, inplace=True)
    complete_norms = pd.concat([complete_norms, club_df], ignore_index=True)


gameweek_df = complete_norms[(complete_norms['GW'] == latest_gameweek) & (complete_norms['Start'] == 1)]


def best16_gk(df):
    gk_df = df[df['Pos'] == 'G']
    gk_df = gk_df.sort_values(by='FPts', ascending=False)
    return gk_df[:8]


def best16_def(df):
    def_df = df[df['Pos'].str.contains("D")]
    def_df = def_df.sort_values(by='FPts', ascending=False)
    return def_df[:40]


def best16_mid(df):
    mid_df = df[df['Pos'].str.contains("M")]
    mid_df = mid_df.sort_values(by='FPts', ascending=False)
    return mid_df[:40]


def best16_fwd(df):
    fwd_df = df[df['Pos'].str.contains("F")]
    fwd_df = fwd_df.sort_values(by='FPts', ascending=False)
    return fwd_df[:24]


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
        remainder = remainder[~remainder['Name'].isin(team_01['Team'])]
        remainder = remainder.drop_duplicates(keep='first')

        team_01 = team_01.append({'Team': remainder.iloc[0, 0], 'Pos': remainder.iloc[0, 2],
                                  'Pts': remainder.iloc[0, 6]}, ignore_index=True)
        remainder = remainder[~remainder['Name'].isin(team_01['Team'])]
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
            remainder = remainder[~remainder['Name'].isin(team_01['Team'])]
            team_01 = team_01.append({'Team': remainder.iloc[0,  0], 'Pos': remainder.iloc[0, 2],
                                      'Pts': remainder.iloc[0, 6]}, ignore_index=True)
        if len(team_01.index) == 8:
            remainder = remainder[~remainder['Name'].isin(team_01['Team'])]
            team_01 = team_01.append({'Team': remainder.iloc[0,  0], 'Pos': remainder.iloc[0, 2],
                                      'Pts': remainder.iloc[0, 6]}, ignore_index=True)
            remainder = remainder[~remainder['Name'].isin(team_01['Team'])]
            team_01 = team_01.append({'Team': remainder.iloc[0, 0], 'Pos': remainder.iloc[0, 2],
                                      'Pts': remainder.iloc[0, 6]}, ignore_index=True)

        remainder = remainder[~remainder['Name'].isin(team_01['Team'])]
        team_01 = team_01.append({'Team': remainder.iloc[0, 0], 'Pos': remainder.iloc[0, 2],
                                  'Pts': remainder.iloc[0, 6]}, ignore_index=True)
        teams[i] = team_01['Team']
        gameweek = gameweek[~gameweek['Name'].isin(team_01['Team'])]

    return teams


team_numbers = np.arange(8, 0, -1)

y = team_creator(gameweek_df, team_numbers)
y.to_excel('the88.xlsx', header=False, sheet_name='GW_{}'.format(latest_gameweek), startcol=1, startrow=6)

