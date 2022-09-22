import pandas as pd
import numpy as np
from datetime import datetime
import xlsxwriter


def create_wb():
    '''
    Create norm scores workbook
    :param df:
    :return:
    '''
    filename = 'FantraxXIs2020_21.xlsx'
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')

    clubs = ['ars', 'avl', 'bha', 'bur', 'che', 'cry', 'eve', 'ful', 'lee', 'lei',
             'liv', 'mci', 'mun', 'new', 'shu', 'sou', 'tot', 'wba', 'whu', 'wol']

    pre_conditions = pd.read_csv('initial_conditions_last_year.csv.csv')

    for club in clubs:
        minute_data = pd.read_csv('minute_data/' + club + '_minute_data.csv')
        df = minute_data.merge(pre_conditions, on='player', how='left')
        write_club_sheet(writer, df, club)

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


start_date = ['2021May22', '2021May18', '2021May14', '2021May07',
              '2021April30', '2021April23', '2021April16', '2021April09', '2021April02',
              '2021March19', '2021March12', '2021March05',
              '2021February26', '2021February19', '2021February12', '2021February05', '2021February02',
              '2021January29', '2021January26', '2021January15', '2021January12', '2021January01',
              '2020December28', '2020December25', '2020December18', '2020December15', '2020December11',
              '2020December04', '2020November27', '2020November20', '2020November06',
              '2020October29', '2020October23', '2020October16', '2020October02',
              '2020September25', '2020September18', '2020September12']

end_date = ['2021May23', '2021May21', '2021May17', '2021May13',
            '2021May06', '2021April29', '2021April22', '2021April15', '2021April08',
            '2021April01', '2021March18', '2021March11',
            '2021March04', '2021February25', '2021February18', '2021February11', '2021February04',
            '2021February01', '2021January28', '2021January25', '2021January14', '2021January11',
            '2020December31', '2020December27', '2020December24', '2020December17', '2020December14',
            '2020December10', '2020December03', '2020November26', '2020November19',
            '2020November05', '2020October29', '2020October22', '2020October15',
            '2020October01', '2020September24', '2020September17']


def obtain_gw_from_date(x, start_date, end_date):

    x['Date'] = x['Date'].str.replace(' ', '')
    x['Date'] = x['Date'].str.replace('Jul', '2021July')
    x['Date'] = x['Date'].str.replace('Jun', '2021June')
    x['Date'] = x['Date'].str.replace('May', '2021May')
    x['Date'] = x['Date'].str.replace('Apr', '2021April')
    x['Date'] = x['Date'].str.replace('Mar', '2021March')
    x['Date'] = x['Date'].str.replace('Feb', '2021February')
    x['Date'] = x['Date'].str.replace('Jan', '2021January')
    x['Date'] = x['Date'].str.replace('Dec', '2020December')
    x['Date'] = x['Date'].str.replace('Nov', '2020November')
    x['Date'] = x['Date'].str.replace('Oct', '2020October')
    x['Date'] = x['Date'].str.replace('Sep', '2020September')
    x['Date'] = x['Date'].str.replace('Aug', '2020August')

    x['Date'] = pd.to_datetime(x['Date'], format='%Y%B%d').dt.strftime('%Y%B%d')
    x['Date'] = pd.to_datetime(x['Date'], format='%Y%B%d')

    for i, date in enumerate(start_date):
        date = datetime.strptime(date, '%Y%B%d')
        x.loc[(x['Date'] >= date) & (x['Date'] <= datetime.strptime(end_date[i], '%Y%B%d')), 'GW'] = 38 - i

    x['Date'] = x['Date'].dt.strftime('%B%d')

    return x


def obtain_fivethirtyeight(x, fivethirtyeight, fixtures):
    '''
    Adds 538 predictions for each game
    :param player_predictions: df
    :param fivethirtyeight: csv
    :return:
    '''

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
        print('CRAPPING OUT WITH THIS MAN', x['Player'])
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
                                'January': 600, 'February': 700, 'March': 800, 'April': 900, 'May': 1000,
                                'June': 1100, 'July': 1200}

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


def write_club_sheet(writer, df, clubname):
    '''
    Write
    :param writer:
    :param df:
    :return:
    '''
    capitalised_clubname = clubname.upper()
    worksheet_name = clubname
    create_blank_sheet(writer, worksheet_name)
    worksheet = writer.sheets[worksheet_name]

    distributions = pd.read_csv('distributions.csv')
    fixtures = pd.read_csv('fixtures.csv')
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

    df = obtain_gw_from_date(df, start_date, end_date)
    df['NormScore'] = df.apply(lambda x: get_norm_score(distributions, x), axis=1)
    df['opp_adj1'] = df.apply(lambda x: obtain_fivethirtyeight(x, fivethirtyeight, fixtures), axis=1)
    df['opp_adj2'] = (df['opp_adj1'] - 33)/10
    df['DateNumeric'] = df['Date'].apply(lambda x: turn_date_numeric(x))
    df.sort_values(by=['club_pos_id', 'player', 'GW', 'DateNumeric'], inplace=True)
    # df['pre-avg'] = df.apply(lambda x: obtain_avg_five(x, df), axis=1)
    df['pre-avg'] = obtain_avg_five(df)
    df['pred'] = df['opp_adj2'] + df['pre-avg']
    df['return'] = df.apply(lambda x: calc_return(x), axis=1)
    df['post-avg'] = df.apply(lambda x: obtain_new_avg_five(x, df), axis=1)
    df['CumReturn'] = df.groupby('player')['return'].cumsum()
    df = df.drop(['Unnamed: 0', 'pre', 'opp_adj1', 'opp_adj2', 'DateNumeric'], axis=1)

    df.to_excel(writer, header=False, sheet_name=worksheet_name, startcol=1, startrow=6)


create_wb()
