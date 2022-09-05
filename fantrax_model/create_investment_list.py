import pandas as pd
import numpy as np

next_gameweek = 7

sheet_names = ['ars', 'avl', 'bha', 'bou', 'brf', 'che', 'cry', 'eve', 'ful', 'lee',
               'lei', 'liv', 'mci', 'mun', 'new', 'not', 'sou', 'tot', 'whu', 'wol']

fixtures = pd.read_csv('fixtures.csv')
fixtures = fixtures[fixtures['GW'] == next_gameweek]

complete_norms = pd.DataFrame(columns=['Name', 'Pos', 'Pos ID', 'Date', 'Team', 'Opp', 'Result', 'FPts', 'Min', 'Start',
                                       'Club Idx', 'GW', 'NormScore', 'Prior AVG', 'Predict', 'Return', 'Post AVG',
                                       'CumReturn'])

for sheet_name in sheet_names:
    capitalised_clubname = sheet_name.upper()
    club_df = pd.read_excel(open('FantraxXIs2022_23.xlsx', 'rb'), sheet_name=sheet_name, skiprows=5)
    club_df.drop(['Unnamed: 0', 'Unnamed: 1'], axis=1, inplace=True)
    complete_norms = pd.concat([complete_norms, club_df], ignore_index=True)


unique_players = complete_norms['Name'].unique()
latest_status = pd.DataFrame(columns=['Name', 'Pos', 'Pos ID', 'Date', 'Team', 'Opp', 'Result', 'FPts', 'Min', 'Start',
                                      'Club Idx', 'GW', 'NormScore', 'Prior AVG', 'Predict', 'Return', 'Post AVG',
                                      'CumReturn'])
for player in unique_players:
    player_df = complete_norms[complete_norms['Name'] == player].tail(1)
    latest_status = pd.concat([latest_status, player_df], ignore_index=True)


def fivethirtyeight_next(x, fivethirtyeight):
    '''
        Adds 538 predictions for each game
        :param player_predictions: df
        :param fivethirtyeight: csv
        :return:
        '''

    gw = x['GW']
    team = x['Team']
    my_fixture = fivethirtyeight[fivethirtyeight['FIXTURE_CODE'].str.contains(team)].reset_index()

    try:
        if my_fixture['AWAY'].item() == team:
            bump = my_fixture['AWAY538'].item()
        else:
            bump = my_fixture['HOME538'].item()

        return bump
    except TypeError:
        print('CRAPPING OUT WITH THIS MAN', x['Player'])
        x['FT8'] = np.nan


latest_status['opp_adj1'] = latest_status.apply(lambda x: fivethirtyeight_next(x, fixtures), axis=1)
latest_status['opp_adj2'] = (latest_status['opp_adj1'] - 33) / 10
latest_status['next fixture'] = latest_status['Post AVG'] + latest_status['opp_adj2']
latest_status = latest_status[latest_status['next fixture'] >= 12].sort_values(by='CumReturn', ascending=False)


# latest_status.to_excel('invest_list.xlsx', header=False, sheet_name='invest_list', startcol=1, startrow=6)

def create_wb(df):
    '''
    Create norm scores workbook
    :param df:
    :return:
    '''
    filename = 'invest_list.xlsx'
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')

    write_invest_sheet(writer, df)

    writer.save()


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


def write_invest_sheet(writer, df):
    '''
    Write the investment list for a given gameweek
    :param writer:
    :param df:
    :return:
    '''

    worksheet_name = 'invest_list'
    create_blank_sheet(writer, worksheet_name)
    worksheet = writer.sheets[worksheet_name]
    ownership = pd.read_csv('ownership.csv')
    df = pd.merge(df, ownership, on='Name', how='left').sort_values(by='CumReturn', ascending=False)

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
    worksheet.write(5, 16, 'PrevPred')
    worksheet.write(5, 17, 'Return')
    worksheet.write(5, 18, 'Post AVG')
    worksheet.write(5, 19, 'CumReturn')
    worksheet.write(5, 20, 'OppRkPct')
    worksheet.write(5, 21, 'OppRkAdj')
    worksheet.write(5, 22, 'NextPred')
    worksheet.write(5, 23, 'Owned')

    # Add a format. Light red fill with dark red text.
    format1 = writer.book.add_format({'bg_color': '#FFC7CE',
                                   'font_color': '#9C0006'})

    # Add a format. Green fill with dark green text.
    format2 = writer.book.add_format({'bg_color': '#C6EFCE',
                                   'font_color': '#006100'})

    other_owners = ['BRZL', 'COF', 'DAMO', 'DK', 'EOC', 'GUN', 'GUN2', 'RORY', 'SUP']

    for i in range(5, 500):
        worksheet.conditional_format('C{0}:X{0}'.format(i), {'type': 'formula',
                                                             'criteria': '=IF($X{0}="HAE","Y","")="Y"'.format(i),
                                                             'format': format2})
        for element in other_owners:
            worksheet.conditional_format('C{0}:X{0}'.format(i), {'type': 'formula',
                                                                 'criteria': '=IF($X{0}="{1}","Y","")="Y"'
                                         .format(i, element),
                                                                 'format': format1})

    df.to_excel(writer, header=False, sheet_name=worksheet_name, startcol=1, startrow=6)


create_wb(latest_status)
