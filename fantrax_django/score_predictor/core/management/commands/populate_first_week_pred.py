'''
A command module to take the season fixture list from .csv to json and upload into database.
'''

from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import FirstWeekPred

import os
import pandas as pd
import numpy as np


class Command(BaseCommand):
    help = 'Update the First Week predicitons with csv data'

    def add_arguments(self, parser):
        parser.add_argument("-f", "--file", dest="file", required=True, type=str,
                            help="Provide a csv filename. (fixtures.csv)")

    def read_data_from_csv(self, file):
        '''
        Read first_week_predictions.csv and build a json object
        :param file:
        :return:
        '''

        path_to_file = os.path.join(os.getcwd(), 'core', 'fixtures', file)

        with open(path_to_file) as f:

            df = pd.read_csv(f)

        return df

    def update_model_data(self, data):
        '''
        Delete PlayerName model data and upload csv data

        :param data:
        :return:
        '''

        FirstWeekPred.objects.all().delete()
        for i, row in enumerate(data.iterrows()):
            FirstWeekPred.objects.create(
                name=row[1]['Players'],
                pred_01=row[1]['Prediction']
            )

    def handle(self, *args, **options):
        '''
        Coordinates all actions

        :param args:
        :param options:
        :return:
        '''

        print('Uploading new First Week Prediction data ...')

        file = options["file"]
        data = self.read_data_from_csv(file)

        with transaction.atomic():
            self.update_model_data(data)
