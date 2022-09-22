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
    filename = 'FantraxXIs2019_20.xlsx'
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')

    clubs = ['ars', 'avl', 'bha', 'bou', 'bur', 'che', 'cry', 'eve', 'lei', 'liv',
             'mci', 'mun', 'new', 'nor', 'shu', 'sou', 'tot', 'wat', 'whu', 'wol']

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


start_date = ['2020July23', '2020July18', '2020July14', '2020July10', '2020July07', '2020July03',
              '2020June26', '2020June23', '2020June13',
              '2020March02', '2020February25', '2020February20', '2020February03',
              '2020January30', '2020January20', '2020January13', '2020January03', '2020January01',
              '2019December28', '2019December23', '2019December17', '2019December10', '2019December06',
              '2019December02', '2019November26', '2019November11', '2019November04',
              '2019October28', '2019October22', '2019October07', '2019October01',
              '2019September23', '2019September17', '2019September02',
              '2019August26', '2019August20', '2019August12', '2019August09']

end_date = ['2020July26', '2020July22', '2020July17', '2020July13', '2020July09', '2020July06',
            '2020July02', '2020June25', '2020June22',
            '2020June12', '2020March01', '2020February24', '2020February19',
            '2020February02', '2020January29', '2020January19', '2020January12', '2020January02',
            '2019December31', '2019December27', '2019December22', '2019December16', '2019December09',
            '2019December05', '2019December01', '2019November25', '2019November10',
            '2019November03', '2019October27', '2019October21', '2019October06',
            '2019September30', '2019September22', '2019September16',
            '2019September01', '2019August25', '2019August19', '2019August11']


def obtain_gw_from_date(x, start_date, end_date):

    x['Date'] = x['Date'].str.replace(' ', '')
    x['Date'] = x['Date'].str.replace('Jul', '2020July')
    x['Date'] = x['Date'].str.replace('Jun', '2020June')
    x['Date'] = x['Date'].str.replace('Apr', '2020April')
    x['Date'] = x['Date'].str.replace('Mar', '2020March')
    x['Date'] = x['Date'].str.replace('Feb', '2020February')
    x['Date'] = x['Date'].str.replace('Jan', '2020January')
    x['Date'] = x['Date'].str.replace('Dec', '2019December')
    x['Date'] = x['Date'].str.replace('Nov', '2019November')
    x['Date'] = x['Date'].str.replace('Oct', '2019October')
    x['Date'] = x['Date'].str.replace('Sep', '2019September')
    x['Date'] = x['Date'].str.replace('Aug', '2019August')

    print(x['Date'], x['player'])
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