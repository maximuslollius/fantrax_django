import os
import pandas as pd
from analysis_app.models import PlayerScoresMinutes
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = 'Update the PlayerNames model with csv data'

    def add_arguments(self, parser):
        parser.add_argument("-f", "--file", dest="file", required=True, type=str,
                            help="Provide a single csv filename.")
        parser.add_argument("-l", "--list", nargs="+", required=True,
                            help="Provide a list of csv filenames.")

    def read_data_from_csv(self, file):
        '''
        Read Squad_Links.csv and build a dataframe
        :param file:
        :return:
        '''

        path_to_file = os.path.join(os.getcwd(), 'analysis_app', 'fixtures',
                                    'player_minute_scores', file)

        with open(path_to_file) as f:

            df = pd.read_csv(f)

        return df

    def update_model_data(self, data):
        '''
        Delete PlayerName model data and upload csv data

        :param data:
        :return:
        '''

        for i, row in enumerate(data.iterrows()):
            PlayerScoresMinutes.objects.create(
                player=row[1]['player'],
                team=row[1]['team'],
                position=row[1]['position'],
                position_id=row[1]['position_id'],
                date=row[1]['date'],
                opposition=row[1]['opp'],
                result=row[1]['date'],
                FPts=row[1]['fpts'],
                minutes=row[1]['min'],
                season=row[1]['season']
            )

    def handle(self, *args, **options):
        '''
        Coordinates all actions

        :param args:
        :param options:
        :return:
        '''

        print('Uploading new season data ...')

        print(options)
        file = options["file"]
        data = self.read_data_from_csv(file)

        with transaction.atomic():
            self.update_model_data(data)
