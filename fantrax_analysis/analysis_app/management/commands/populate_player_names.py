import os
import pandas as pd
from analysis_app.models import PlayerNames
from django.db import transaction
from django.core.management.base import BaseCommand
from pathlib import Path


class Command(BaseCommand):
    help = 'Update the PlayerNames model with csv data'

    def add_arguments(self, parser):
        parser.add_argument("-f", "--file", dest="file", required=True, type=str,
                            help="Provide a csv filename. (Squad_Links.csv)")

    def read_data_from_csv(self, file):
        '''
        Read Squad_Links.csv and build a dataframe
        :param file:
        :return:
        '''

        path_to_file = os.path.join(os.getcwd(), 'analysis_app', 'fixtures', file)

        with open(path_to_file) as f:

            df = pd.read_csv(f)

        return df

    def update_model_data(self, data):
        '''
        Delete PlayerName model data and upload csv data

        :param data:
        :return:
        '''

        PlayerNames.objects.all().delete()
        for i, row in enumerate(data.iterrows()):
            print(row[1]['player'])
            PlayerNames.objects.create(
                id=(i + 1),
                name=row[1]['player'],
                team=row[1]['club'],
                position=row[1]['pos'],
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
