import pandas as pd
import numpy as np
from datetime import datetime
from normalizer.get_norm_params import get_season_shorthand, get_current_clubs, get_gameweek_dates
import os
import argparse
import xlsxwriter

# Take in arguments from the command line:
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--season", default="2022-23", help="The EPL Season of interest")
parser.add_argument("-ct", "--condtype", default="investment", help="The EPL Season of interest")
args = parser.parse_args()


def create_wb(season, conditional_type):
    '''
    Create norm scores workbook
    :param season: The current season
    :param conditional_type: Conditonal formatting either investment active only or all starts.
    :return:
    '''
    season_short_hand = get_season_shorthand(season)
    filename = os.path.join('output', 'FantraxXIs20{}.xlsx'.format(season_short_hand))
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    clubs = get_current_clubs(season)

    pre_conditions = pd.read_csv(os.path.join('initial_conditions', 'ic_{}'.format(season_short_hand),
                                              'initial_conditions.csv'))

    for club in clubs:
        minute_data = pd.read_csv(os.path.join('minute_data', 'minute_data_{}'.format(season_short_hand), club +
                                               '_minute_data.csv'))
        df = minute_data.merge(pre_conditions, on='player', how='left')
        write_club_sheet(writer, df, club, season, conditional_type)

    writer.save()


def get_norm_score(distributions, x):
    act_fpts = x['FPts']
    minutes = x['Min']

    if minutes == 90:
        norm_score = act_fpts
    else:
        distributions = distributions[(distributions['minutes_played'].astype(float) == minutes)
                                      & (distributions['actual_score'].astype(float) <= act_fpts)]
        if distributions.empty:
            norm_score = 0
        else:
            last_row = len(distributions.index) - 1
            norm_score = distributions.reset_index(drop=True).loc[last_row, 'extrapolated_score']
    return norm_score


def obtain_gw_from_date(x, start_date, end_date, season):

    year = {'2019-20': ['2019', '2020'], '2020-21': ['2020', '2021'],
            '2021-22': ['2021', '2022'], '2022-23': ['2022', '2023']}

    my_year = year[season]

    x['Date'] = x['Date'].str.replace(' ', '')
    x['Date'] = x['Date'].str.replace('Jul', '{}July'.format(my_year[1]))
    x['Date'] = x['Date'].str.replace('Jun', '{}June'.format(my_year[1]))
    x['Date'] = x['Date'].str.replace('May', '{}May'.format(my_year[1]))
    x['Date'] = x['Date'].str.replace('Apr', '{}April'.format(my_year[1]))
    x['Date'] = x['Date'].str.replace('Mar', '{}March'.format(my_year[1]))
    x['Date'] = x['Date'].str.replace('Feb', '{}February'.format(my_year[1]))
    x['Date'] = x['Date'].str.replace('Jan', '{}January'.format(my_year[1]))
    x['Date'] = x['Date'].str.replace('Dec', '{}December'.format(my_year[0]))
    x['Date'] = x['Date'].str.replace('Nov', '{}November'.format(my_year[0]))
    x['Date'] = x['Date'].str.replace('Oct', '{}October'.format(my_year[0]))
    x['Date'] = x['Date'].str.replace('Sep', '{}September'.format(my_year[0]))
    x['Date'] = x['Date'].str.replace('Aug', '{}August'.format(my_year[0]))

    x['Date'] = pd.to_datetime(x['Date'], format='%Y%B%d').dt.strftime('%Y%B%d')
    x['Date'] = pd.to_datetime(x['Date'], format='%Y%B%d')

    for i, date in enumerate(start_date):
        date = datetime.strptime(date, '%Y%B%d')
        x.loc[(x['Date'] >= date) & (x['Date'] <= datetime.strptime(end_date[i], '%Y%B%d')), 'GW'] = 38 - i

    x['Date'] = x['Date'].dt.strftime('%B%d')

    return x


def obtain_fivethirtyeight(x, fivethirtyeight, fixtures):
    """
    Adds 538 predictions for each game
    :param player_predictions: df
    :param fivethirtyeight: csv
    :return:
    """

    gw = x['GW']

    try:
        if x['opp'][0] == '@':
            away_team = x['team']
            home_team = x['opp'][1:]
            try:
                my_538 = fivethirtyeight[(fivethirtyeight['GW'] == gw) & (fivethirtyeight['HOME'] == home_team) & (
                        fivethirtyeight['AWAY'] == away_team)].reset_index()
                bump = my_538.loc[0, 'AWAY538']
            except KeyError:
                my_538 = fixtures[(fixtures['GW'] == gw) & (fixtures['HOME'] == home_team) & (
                        fixtures['AWAY'] == away_team)].reset_index()
                bump = my_538.loc[0, 'AWAY538']

        else:
            home_team = x['team']
            away_team = x['opp']
            try:
                my_538 = fivethirtyeight[(fivethirtyeight['GW'] == gw) & (fivethirtyeight['HOME'] == home_team) & (
                    fivethirtyeight['AWAY'] == away_team)].reset_index()
                bump = my_538.loc[0, 'HOME538']
            except KeyError:
                my_538 = fixtures[(fixtures['GW'] == gw) & (fixtures['HOME'] == home_team) & (
                        fixtures['AWAY'] == away_team)].reset_index()
                bump = my_538.loc[0, 'HOME538']

        return bump

    except TypeError:
        print('ERROR WITH THIS MAN', x['Player'])
        x['FT8'] = np.nan


def obtain_avg_five(df):
    avg_five = list()
    unique_players = df.drop_duplicates(subset='player')

    for i, row in unique_players.iterrows():
        player_df = df[df['player'] == row['player']]

        if len(player_df.index) == 1:
            avg_five.append(row['pre'])
        elif len(player_df.index) == 2:
            avg_five.append((4*row['pre'] + player_df['NormScore'].iloc[0])/5)
            avg_five.append(row['pre'])
        elif len(player_df.index) == 3:
            avg_five.append((3*row['pre'] + player_df['NormScore'].iloc[0] + player_df['NormScore'].iloc[1])/5)
            avg_five.append((4*row['pre'] + player_df['NormScore'].iloc[0])/5)
            avg_five.append(row['pre'])
        elif len(player_df.index) == 4:
            avg_five.append((2*row['pre'] + player_df['NormScore'].iloc[0] + player_df['NormScore'].iloc[1]
                             + player_df['NormScore'].iloc[2])/5)
            avg_five.append((3*row['pre'] + player_df['NormScore'].iloc[0] + player_df['NormScore'].iloc[1])/5)
            avg_five.append((4*row['pre'] + player_df['NormScore'].iloc[0])/5)
            avg_five.append(row['pre'])
        elif len(player_df.index) == 5:
            avg_five.append((row['pre'] + player_df['NormScore'].iloc[0] + player_df['NormScore'].iloc[1]
                             + player_df['NormScore'].iloc[2] + player_df['NormScore'].iloc[3])/5)
            avg_five.append((2*row['pre'] + player_df['NormScore'].iloc[0] + player_df['NormScore'].iloc[1]
                             + player_df['NormScore'].iloc[2])/5)
            avg_five.append((3*row['pre'] + player_df['NormScore'].iloc[0] + player_df['NormScore'].iloc[1])/5)
            avg_five.append((4*row['pre'] + player_df['NormScore'].iloc[0])/5)
            avg_five.append(row['pre'])
        else:
            rolling_avg_series = player_df['NormScore'].rolling(window=5).mean().dropna()
            rolling_avg_series = rolling_avg_series.to_list()
            rolling_avg_series.pop()
            rolling_avg_series.reverse()
            for x in rolling_avg_series:
                avg_five.append(x)
            avg_five.append((row['pre'] + player_df['NormScore'].iloc[0] + player_df['NormScore'].iloc[1]
                             + player_df['NormScore'].iloc[2] + player_df['NormScore'].iloc[3])/5)
            avg_five.append((2*row['pre'] + player_df['NormScore'].iloc[0] + player_df['NormScore'].iloc[1]
                             + player_df['NormScore'].iloc[2])/5)
            avg_five.append((3*row['pre'] + player_df['NormScore'].iloc[0] + player_df['NormScore'].iloc[1])/5)
            avg_five.append((4*row['pre'] + player_df['NormScore'].iloc[0])/5)
            avg_five.append(row['pre'])

    avg_five = pd.Series(avg_five)

    return avg_five


def obtain_new_avg_five(x, df):
    df = df[df['player'] == x['player']]

    if len(df.index) == 1:
        avg_five = (4*x['pre'] + x['NormScore'])/5
    elif len(df.index) == 2:
        avg_five = (3*x['pre'] + df['NormScore'].iloc[0] + df['NormScore'].iloc[1])/5
    elif len(df.index) == 3:
        avg_five = (2*x['pre'] + df['NormScore'].iloc[0] + df['NormScore'].iloc[1] + df['NormScore'].iloc[2])/5
    elif len(df.index) == 4:
        avg_five = (x['pre'] + df['NormScore'].iloc[0] + df['NormScore'].iloc[1] + df['NormScore'].iloc[2]
                    + df['NormScore'].iloc[3])/5
    else:
        df = df.iloc[-5:]
        avg_five = (df['NormScore'].mean())

    return avg_five


def calc_return(x):
    '''
    Calculates the return on investment, only if they were investment grade (12+ pred)
    :param x: dataframe row
    :return:
    '''

    if x['pred'] >= 12 and x['starts'] == 1:
        x = x['FPts'] - 12
    else:
        x = 0

    return x


def turn_date_numeric(x):
    '''
    Calculates the return on investment, only if they were investment grade (12+ pred)
    :param x: dataframe row
    :return:
    '''

    season_months_to_numeric = {'August': 100, 'September': 200, 'October': 300, 'November': 400, 'December': 500,
                                'January': 600, 'February': 700, 'March': 800, 'April': 900, 'May': 1000, 'June': 1100,
                                'July': 1200}

    month = x[:-2]
    day = float(x[-2:])
    month_numeric = season_months_to_numeric[month]
    x = month_numeric + day

    return x


def create_blank_sheet(writer, worksheet_name, show_gridlines=False):
    '''
    Creates blank sheet
    :param writer:
    :param worksheet_name:
    :param show_gridlines:
    :return:
    '''

    gridlines_values = 1 if show_gridlines else 2
    df = pd.DataFrame({})
    df.to_excel(writer, header=False, sheet_name=worksheet_name, startcol=1, startrow=6)
    writer.sheets[worksheet_name].hide_gridlines(gridlines_values)


def write_club_sheet(writer, df, clubname, season, conditional_type):
    '''
    Write
    :param writer: excel writer engine
    :param df: player minute df
    :param clubname: 3 letter club abbreviation
    :param season: the current season
    :return:
    '''
    capitalised_clubname = clubname.upper()
    worksheet_name = clubname
    create_blank_sheet(writer, worksheet_name)
    worksheet = writer.sheets[worksheet_name]

    distributions = pd.read_csv('distributions.csv')
    season_short_hand = get_season_shorthand(season)
    fixtures = pd.read_csv(os.path.join('fixtures', 'fixtures_{}'.format(season_short_hand), 'fixtures.csv'))
    fivethirtyeight = fixtures[fixtures['FIXTURE_CODE'].str.contains(capitalised_clubname)]
    df.rename(columns={"min": "Min", "fpts": "FPts", "date": "Date", "start_x": "start",
                       "Unnamed: 0_x": "Unnamed: 0", "Unnamed: 0_y": "Unnamed: 0"}, inplace=True)

    worksheet.write(0, 0, 'Club Name')
    worksheet.write(0, 1, capitalised_clubname)
    worksheet.write(5, 2, 'Name')
    worksheet.write(5, 3, 'Pos')
    worksheet.write(5, 4, 'Pos ID')
    worksheet.write(5, 5, 'Date')
    worksheet.write(5, 6, 'Team')
    worksheet.write(5, 7, 'Opp')
    worksheet.write(5, 8, 'Result')
    worksheet.write(5, 9, 'FPts')
    worksheet.write(5, 10, 'Min')
    worksheet.write(5, 11, 'Start')
    worksheet.write(5, 12, 'Club Idx')
    worksheet.write(5, 13, 'GW')
    worksheet.write(5, 14, 'NormScore')
    worksheet.write(5, 15, 'Prior AVG')
    worksheet.write(5, 16, 'Predict')
    worksheet.write(5, 17, 'Return')
    worksheet.write(5, 18, 'Post AVG')
    worksheet.write(5, 19, 'CumReturn')

    gw_dates = get_gameweek_dates(season)
    df = obtain_gw_from_date(df, gw_dates['start_date'], gw_dates['end_date'], season)
    df['NormScore'] = df.apply(lambda x: get_norm_score(distributions, x), axis=1)
    df['opp_adj1'] = df.apply(lambda x: obtain_fivethirtyeight(x, fivethirtyeight, fixtures), axis=1)
    df['opp_adj2'] = (df['opp_adj1'] - 33)/10
    df['DateNumeric'] = df['Date'].apply(lambda x: turn_date_numeric(x))
    df.sort_values(by=['club_pos_id', 'player', 'GW', 'DateNumeric'], inplace=True)
    df['pre-avg'] = obtain_avg_five(df)
    df['pred'] = df['opp_adj2'] + df['pre-avg']
    df['return'] = df.apply(lambda x: calc_return(x), axis=1)
    df['post-avg'] = df.apply(lambda x: obtain_new_avg_five(x, df), axis=1)
    df['CumReturn'] = df.groupby('player')['return'].cumsum()
    df = df.drop(['Unnamed: 0', 'pre', 'opp_adj1', 'opp_adj2', 'DateNumeric'], axis=1)

    # Add a format. Light red fill with dark red text.
    format1 = writer.book.add_format({'bg_color': '#FFC7CE',
                                   'font_color': '#9C0006'})

    # Add a format. Green fill with dark green text.
    format2 = writer.book.add_format({'bg_color': '#C6EFCE',
                                   'font_color': '#006100'})

    # Add a format. Amber fill with dark amber text.
    format3 = writer.book.add_format({'bg_color': '#FFEB9C',
                                   'font_color': '#9C6500'})

    if conditional_type == 'investment':
        for i in range(7, 500):
            worksheet.conditional_format('C{0}:T{0}'.format(i), {'type': 'formula',
                                                                 'criteria': '=IF(AND($L{0}>0, '
                                                                             '$Q{0}>=12,$R{0}>=0),"Y","")="Y"'
                                         .format(i), 'format': format2})
            worksheet.conditional_format('C{0}:T{0}'.format(i), {'type': 'formula',
                                                                 'criteria': '=IF(AND($L{0}>0, '
                                                                             '$Q{0}>=12,$R{0}<-2),"Y","")="Y"'
                                         .format(i), 'format': format1})
            worksheet.conditional_format('C{0}:T{0}'.format(i), {'type': 'formula',
                                                                 'criteria': '=IF(AND($L{0}>0, $Q{0}>=12,'
                                                                             '$R{0}<0, $R{0}>=-2),"Y","")="Y"'
                                         .format(i), 'format': format3})
    else:
        for i in range(7, 500):
            worksheet.conditional_format('C{0}:T{0}'.format(i), {'type': 'formula',
                                                                 'criteria': '=IF(AND($L{0}>0, '
                                                                             '$J{0}>=12),"Y","")="Y"'
                                         .format(i), 'format': format2})
            worksheet.conditional_format('C{0}:T{0}'.format(i), {'type': 'formula',
                                                                 'criteria': '=IF(AND($L{0}>0, '
                                                                             '$J{0}<10),"Y","")="Y"'
                                         .format(i), 'format': format1})
            worksheet.conditional_format('C{0}:T{0}'.format(i), {'type': 'formula',
                                                                 'criteria': '=IF(AND($L{0}>0,'
                                                                             '$J{0}>=10),"Y","")="Y"'
                                         .format(i), 'format': format3})

    df.to_excel(writer, header=False, sheet_name=worksheet_name, startcol=1, startrow=6)


create_wb(args.season, args.condtype)
