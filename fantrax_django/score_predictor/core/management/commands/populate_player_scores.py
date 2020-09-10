'''
A command module to take player names from .csv to json and upload into database.
'''

from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import PlayerScores, PlayerNames

import os
import pandas as pd
import numpy as np
import re


class Command(BaseCommand):
    help = 'Update the PlayerScores model with csv data'

    def read_data_from_csv(self, file):
        '''
        Read first_week_predictions.csv and build a json object
        :param file:
        :return:
        '''

        path_to_folder = os.path.join(os.getcwd(), 'core', 'fixtures', 'gameweeks')

        names = PlayerNames.objects.values_list('name', 'team', 'position')
        merged_df = pd.DataFrame(list(names), columns=['Player', 'Team', 'Position'])

        names_in_file = []
        for filename in os.listdir(path_to_folder):
            names_in_file.append(filename)
            names_in_file.sort()

        gameweek_files = []
        for f in names_in_file:
            print(f)
            df = pd.read_csv(path_to_folder + '/' + f)
            gameweek_files.append(df)

        for i, df in enumerate(gameweek_files):
            df = df[['Player', 'Team', 'Position', 'Opponent', 'FPts']]
            renamer = {'Team': 'Team_{0}'.format(i+1), 'Position': 'Position_{0}'.format(i+1),
                   'Opponent': 'Opponent_{0}'.format(i+1), 'FPts': 'FPts_{0}'.format(i+1)}
            df.rename(columns=renamer, inplace=True)
            merged_df = pd.merge(merged_df, df, how='outer', on=['Player'])
            merged_df.drop_duplicates(inplace=True, keep='last')

        # Attempt at regex so we only have 1 Team, Position columns
        r = re.compile(r'Team')
        columns_to_drop = list(filter(r.match, merged_df.columns))
        columns_to_drop = columns_to_drop[:-1]
        merged_df.drop(columns_to_drop, axis=1, inplace=True)

        r = re.compile(r'Position')
        columns_to_drop = list(filter(r.match, merged_df.columns))
        columns_to_drop = columns_to_drop[:-1]
        merged_df.drop(columns_to_drop, axis=1, inplace=True)

        renamer_2 = {'Team_{0}'.format(len(gameweek_files)): 'Team',
                   'Position_{0}'.format(len(gameweek_files)): 'Position'}
        merged_df.rename(columns=renamer_2, inplace=True)

        position_integer = {'G': 1, 'D': 2, 'D,M': 3, 'M': 4, 'M,F': 5, 'F': 6}
        merged_df['Position Integer'] = merged_df['Position'].map(position_integer)
        merged_df = merged_df.sort_values(by=['Team', 'Position Integer', 'Player']).fillna(0)

        return merged_df

    def update_model_data(self, data):
        '''
        Delete PlayerName model data and upload csv data

        :param data:
        :return:
        '''

        PlayerScores.objects.all().delete()
        for i, row in enumerate(data.iterrows()):
            PlayerScores.objects.create(
                id=(i + 1),
                name=row[1]['Player'],
                team=row[1]['Team'],
                position=row[1]['Position'],
                position_id=row[1]['Position Integer'],
                gw_01 = row[1]['FPts_1'],
                gw_02 = row[1]['FPts_2'],
                gw_03 = row[1]['FPts_3'],
                gw_04 = row[1]['FPts_4'],
                gw_05 = row[1]['FPts_5'],
                gw_06 = row[1]['FPts_6'],
                gw_07 = row[1]['FPts_7'],
                gw_08 = row[1]['FPts_8'],
                gw_09 = row[1]['FPts_9'],
                gw_10 = row[1]['FPts_10'],
                gw_11 = row[1]['FPts_11'],
                gw_12 = row[1]['FPts_12'],
                gw_13 = row[1]['FPts_13'],
                gw_14 = row[1]['FPts_14'],
                gw_15 = row[1]['FPts_15'],
                gw_16 = row[1]['FPts_16'],
                gw_17 = row[1]['FPts_17'],
                gw_18 = row[1]['FPts_18'],
                gw_19 = row[1]['FPts_19'],
                gw_20 = row[1]['FPts_20'],
                gw_21 = row[1]['FPts_21'],
                gw_22 = row[1]['FPts_22'],
                gw_23 = row[1]['FPts_23'],
                gw_24 = row[1]['FPts_24'],
                gw_25 = row[1]['FPts_25'],
            )

    def handle(self, *args, **options):
        '''
        Coordinates all actions

        :param args:
        :param options:
        :return:
        '''

        print('Uploading new Player Scores data ...')
        data = self.read_data_from_csv(options)

        with transaction.atomic():
            self.update_model_data(data)
