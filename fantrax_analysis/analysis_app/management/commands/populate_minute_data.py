'''
A command module to take the season fixture list from .csv to json and upload into database.
'''

from django.core.management.base import BaseCommand
from django.db import transaction
from analysis_app.models import PlayerScoresMinutes

import os
import pandas as pd
import numpy as np


class Command(BaseCommand):
    help = 'Update the Player Minutes model with csv data'

    def add_arguments(self, parser):
        parser.add_argument("-f", "--file", dest="file", required=True, type=str,
                            help="Provide a csv filename. (arsenal.csv)")

    def read_data_from_csv(self, file):
        '''
        Read first_week_predictions.csv and build a json object
        :param file:
        :return:
        '''

        path_to_file = os.path.join(os.getcwd(), 'analysis_app', 'fixtures', 'gw_fixtures', file)

        with open(path_to_file) as f:

            df = pd.read_csv(f)
            df['link'] = df['HOME'] + df['AWAY']

        return df

    def update_model_data(self, data):
        '''
        Delete PlayerName model data and upload csv data

        :param data:
        :return:
        '''

        PlayerScoresMinutes.objects.all().delete()
        for i, row in enumerate(data.iterrows()):
            PlayerScoresMinutes.objects.create(
                id=i,
                gw=row[1]['GW'],
                home_team=row[1]['HOME'],
                away_team=row[1]['AWAY'],
                home_pct=row[1]['HOME_SCORE'],
                away_pct=row[1]['AWAY_SCORE'],
            )

    def handle(self, *args, **options):
        '''
        Coordinates all actions

        :param args:
        :param options:
        :return:
        '''

        print('Uploading new Season Fixtures data ...')

        file = options["file"]

        # define the folder paths
        path_to_minute_folders = os.path.join(os.getcwd(), 'analysis_app', 'minute_data')
        folders = ['minute_data_19_20', 'minute_data_20_21', 'minute_data_21_22', 'minute_data_22_23']

        # initialize an empty dataframe to hold the concatenated data
        df_concat = pd.DataFrame()

        # loop through each folder
        for folder in folders:
            # get a list of all the CSV files in the folder
            csv_files = [f for f in os.path.join(path_to_minute_folders, folder) if f.endswith('.csv')]

            # loop through each CSV file and concatenate to the dataframe
            for csv_file in csv_files:
                # read the CSV file into a dataframe
                single_season_df = pd.read_csv(os.path.join(path_to_minute_folders, folder, csv_file))

                # concatenate the dataframe to the overall dataframe
                df_concat = pd.concat([df_concat, single_season_df], ignore_index=True)

        # print the final concatenated dataframe
        print(df_concat.head(25))
        data = self.read_data_from_csv(file)

        with transaction.atomic():
            self.update_model_data(data)
