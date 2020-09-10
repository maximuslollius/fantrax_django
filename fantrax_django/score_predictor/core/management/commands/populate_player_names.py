'''
A command module to take player names from .csv to json and upload into database.
'''

from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import PlayerNames

import os
import pandas as pd
import numpy as np


class Command(BaseCommand):
    help = 'Update the PlayerNames model with csv data'

    def add_arguments(self, parser):
        parser.add_argument("-f", "--file", dest="file", required=True, type=str,
                            help="Provide a csv filename. (first_week_predictions.csv)")

    def read_data_from_csv(self, file):
        '''
        Read first_week_predictions.csv and build a json object
        :param file:
        :return:
        '''

        path_to_file = os.path.join(os.getcwd(), 'core', 'fixtures', file)

        with open(path_to_file) as f:

            df = pd.read_csv(f)
            df = df[['Player', 'Team', 'Position']]
            position_integer = {'G':1, 'D': 2, 'D,M': 3, 'M': 4, 'M,F': 5, 'F': 6}
            df['Position Integer'] = df['Position'].map(position_integer)
            df = df.sort_values(by=['Team', 'Position Integer', 'Player'])

        return df

    def update_model_data(self, data):
        '''
        Delete PlayerName model data and upload csv data

        :param data:
        :return:
        '''

        PlayerNames.objects.all().delete()
        for i, row in enumerate(data.iterrows()):
            PlayerNames.objects.create(
                id=(i + 1),
                name=row[1]['Player'],
                team=row[1]['Team'],
                position=row[1]['Position'],
                position_id=row[1]['Position Integer']
            )

    def handle(self, *args, **options):
        '''
        Coordinates all actions

        :param args:
        :param options:
        :return:
        '''

        print('Uploading new Player Names data ...')

        file = options["file"]
        data = self.read_data_from_csv(file)

        with transaction.atomic():
            self.update_model_data(data)
