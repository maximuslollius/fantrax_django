'''
A command module to take 538 table predictions from .csv to json and upload into database.
'''

from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import PredictedTable

import os
import pandas as pd
import numpy as np


class Command(BaseCommand):
    help = 'Update the PlayerNames model with csv data'

    def add_arguments(self, parser):
        parser.add_argument("-f", "--file", dest="file", required=True, type=str,
                            help="Provide a csv filename. (rankings.csv)")

    def read_data_from_csv(self, file):
        '''
        Read first_week_predictions.csv and build a json object
        :param file:
        :return:
        '''

        path_to_file = os.path.join(os.getcwd(), 'core', 'fixtures', 'predicted_league_tables', file)

        with open(path_to_file) as f:

            df = pd.read_csv(f)

        return df

    def update_model_data(self, data):
        '''
        Delete PlayerName model data and upload csv data

        :param data:
        :return:
        '''

        PredictedTable.objects.all().delete()
        for i, row in enumerate(data.iterrows()):
            PredictedTable.objects.create(
                gw=row[1]['Position'],
                gw_01=row[1]['GW_01'],
                gw_02=row[1]['GW_02'],
                gw_03=row[1]['GW_03'],
                gw_04=row[1]['GW_04'],
                gw_05=row[1]['GW_05'],
                gw_06=row[1]['GW_06'],
                gw_07=row[1]['GW_07'],
                gw_08=row[1]['GW_08'],
                gw_09=row[1]['GW_09'],
                gw_10=row[1]['GW_10'],
                gw_11=row[1]['GW_11'],
                gw_12=row[1]['GW_12'],
                gw_13=row[1]['GW_13'],
                gw_14=row[1]['GW_14'],
                gw_15=row[1]['GW_15'],
                gw_16=row[1]['GW_16'],
                gw_17=row[1]['GW_17'],
                gw_18=row[1]['GW_18'],
                gw_19=row[1]['GW_19'],
                gw_20=row[1]['GW_20'],
                gw_21=row[1]['GW_21'],
                gw_22=row[1]['GW_22'],
                gw_23=row[1]['GW_23'],
                gw_24=row[1]['GW_24'],
                gw_25=row[1]['GW_25'],
                gw_26=row[1]['GW_26'],
                gw_27=row[1]['GW_27'],
                gw_28=row[1]['GW_28'],
                gw_29=row[1]['GW_29'],
                gw_30=row[1]['GW_30'],
            )

    def handle(self, *args, **options):
        '''
        Coordinates all actions

        :param args:
        :param options:
        :return:
        '''

        print('Uploading Predicted Tables ...')

        file = options["file"]
        data = self.read_data_from_csv(file)

        with transaction.atomic():
            self.update_model_data(data)
