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
    filename = 'FantraxXIs2021_22.xlsx'
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')

    clubs = ['ars', 'avl', 'brf', 'bha', 'bur', 'che', 'cry', 'eve', 'lee', 'lei',
             'liv', 'mci', 'mun', 'new', 'nor', 'sou', 'tot', 'wat', 'whu', 'wol']

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


start_date = ['2022May20', '2022May13', '2022May06',
              '2022April29', '2022April22', '2022April15', '2022April08', '2022April01',
              '2022March18', '2022March11', '2022March04',
              '2022February25', '2022February18', '2022February11', '2022February08',
              '2022January21', '2022January14', '2022January01',
              '2021December28', '2021December25', '2021December17', '2021December14', '2021December10',
              '2021December03', '2021November30', '2021November26', '2021November19', '2021November05',
              '2021October29', '2021October22', '2021October15', '2021October01',
              '2021September24', '2021September17', '2021September10',
              '2021August27', '2021August20', '2021August13']

end_date = ['2022May22', '2022May19', '2022May12',
            '2022May05', '2022April28', '2022April21', '2022April14', '2022April07',
            '2022March31', '2022March17', '2022March10',
            '2022March03', '2022February24', '2022February17', '2022February10',
            '2022February07', '2022January20', '2022January13',
            '2021December31', '2021December27', '2021December24', '2021December16', '2021December13',
            '2021December09', '2021December02', '2021November29', '2021November25', '2021November18',
            '2021November04', '2021October28', '2021October21', '2021October14',
            '2021September30', '2021September23', '2021September16',
            '2021September09', '2021August26', '2021August19']


def obtain_gw_from_date(x, start_date, end_date):

    x['Date'] = x['Date'].str.replace(' ', '')
    x['Date'] = x['Date'].str.replace('Jul', '2022July')
    x['Date'] = x['Date'].str.replace('Jun', '2022June')
    x['Date'] = x['Date'].str.replace('May', '2022May')
    x['Date'] = x['Date'].str.replace('Apr', '2022April')
    x['Date'] = x['Date'].str.replace('Mar', '2022March')
    x['Date'] = x['Date'].str.replace('Feb', '2022February')
    x['Date'] = x['Date'].str.replace('Jan', '2022January')
    x['Date'] = x['Date'].str.replace('Dec', '2021December')
    x['Date'] = x['Date'].str.replace('Nov', '2021November')
    x['Date'] = x['Date'].str.replace('Oct', '2021October')
    x['Date'] = x['Date'].str.replace('Sep', '2021September')
    x['Date'] = x['Date'].str.replace('Aug', '2021August')

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
                                'January': 600, 'February': 700, 'March': 800, 'April': 900, 'May': 1000}

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
