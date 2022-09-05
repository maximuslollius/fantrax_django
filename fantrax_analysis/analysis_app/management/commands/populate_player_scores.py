from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import time
from datetime import datetime
import os
import pandas as pd
from core.models import PlayerScores
from django.core.management.base import BaseCommand
from django.db import transaction
from django.core.exceptions import ValidationError


capabilities = DesiredCapabilities().FIREFOX
capabilities["marionette"] = True
browser = webdriver.Firefox(executable_path="/usr/local/Cellar/geckodriver/0.27.0/bin/geckodriver")

options = Options()
options.headless = True
startTime = datetime.now()


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

        path_to_file = os.path.join(os.getcwd(), 'core', 'fixtures', file)

        with open(path_to_file) as f:

            df = pd.read_csv(f)

        return df

    def fantrax_login(self):
        '''
        A login to fantrax so when we try to get the player bio page we are already logged in
        :return:
        '''
        browser.get('https://www.fantrax.com/login')
        time.sleep(10)
        Input_Username = browser.find_element_by_id('mat-input-0')
        Input_Username.send_keys('haezzer@gmail.com')
        Input_Password = browser.find_element_by_id('mat-input-1')
        Input_Password.send_keys('dw9fvq')
        # Create click button object from above Xpath
        Click_button = browser.find_elements_by_class_name('mat-raised-button')
        # Click button to log onto page
        Click_button[1].click()
        # put in 5 second delay so page can load
        time.sleep(10)

    def obtain_results_table(self, link, player):
        '''
        Takes a player bio link and obtains the fantrax data table that is on that page/
        :param link: url for a fantrax player
        :return: df
        '''
        try:
            browser.get(link)
            time.sleep(10)
            # We want to go to Games(Fantasy) tab:
            nav_bar = browser.find_elements_by_class_name('tabs__item')
            time.sleep(10)
            try:
                browser.execute_script("arguments[0].click();", nav_bar[3])
            except IndexError:
                time.sleep(60)
                browser.execute_script("arguments[0].click();", nav_bar[3])
        except IndexError:
            time.sleep(60)
            self.fantrax_login()
            browser.get(link)
            time.sleep(10)
            # We want to go to Games(Fantasy) tab:
            nav_bar = browser.find_elements_by_class_name('tabs__item')
            time.sleep(10)
            try:
                browser.execute_script("arguments[0].click();", nav_bar[3])
            except IndexError:
                time.sleep(60)
                browser.execute_script("arguments[0].click();", nav_bar[3])

        time.sleep(10)
        # Locate table and turn to dataframe.
        form_table = browser.find_elements_by_class_name('sticky-table')
        try:
            df = pd.read_html(form_table[0].get_attribute('outerHTML'))
            df = df[0].rename({"Unnamed: 0": "Date", "Unnamed: 1": "Team", "Unnamed: 2": "Opp",
                               "Unnamed: 3": "Score", "Unnamed: 4": "FPts", "Unnamed: 5": "Min"}, axis=1)
            df['player'] = player

        except ImportError:
            df = pd.DataFrame(columns=["player", "Date", "Opp", "Score", "FPts", "Min"])

        except IndexError:
            df = pd.DataFrame(columns=["player", "Date", "Opp", "Score", "FPts", "Min"])

        return df[["player", "Date", "Opp", "Score", "FPts", "Min"]]

    def update_model_data(self, data):
        '''
        Delete PlayerName model data and upload csv data

        :param data:
        :return:
        '''

        for i, row in enumerate(data.iterrows()):
            PlayerScores.objects.create(
                name=row[1]['player'],
                team=row[1]['team'],
                position=row[1]['position'],
                position_id=row[1]['position_id'],
                date=row[1]['date'],
                opposition=row[1]['opp'],
                result=row[1]['date'],
                FPts=row[1]['fpts'],
                minutes=row[1]['min'],
            )

    def handle(self, *args, **options):
        '''
        Coordinates all actions

        :param args:
        :param options:
        :return:
        '''

        print('Uploading new Player Names data ...')
        # PlayerScores.objects.all().delete()

        file = options["file"]
        squad_links = self.read_data_from_csv(file)

        self.fantrax_login()
        data = pd.DataFrame(columns=['player', 'team', 'position', ])
        data['player'] = squad_links["Player"]
        data['team'] = squad_links["Team"]
        data['position'] = squad_links["Position"]
        data['position_id'] = squad_links["Position ID"]

        # for i in range(len(data)):
        for i in range(179, len(data)):
            result = None
            while result is None:
                try:
                    link = squad_links.loc[i, "Link"]
                    player = data.loc[i, 'player']
                    print('Scraping player:', data.loc[i, 'player'])
                    temp_df = pd.DataFrame(columns=["player", "date", "opp", "score", "fpts", "min"])
                    temp_df[["player", "date", "opp", "score", "fpts", "min"]] = self.obtain_results_table(link, player)
                    db_data = pd.merge(data, temp_df, on='player', how='inner')
                    print(db_data)
                    db_data[["player", "date", "opp", "score"]] = db_data[["player", "date", "opp", "score"]].fillna('')
                    db_data[["fpts", "min"]] = db_data[["fpts", "min"]].fillna(0)

                    with transaction.atomic():
                        self.update_model_data(db_data)

                    result = 1
                except IndexError:
                    pass
                except ImportError:
                    pass
                except ValidationError:
                    pass




