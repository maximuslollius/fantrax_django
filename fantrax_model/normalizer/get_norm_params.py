import pandas as pd
import numpy as np
from datetime import datetime


def get_season_shorthand(season):
    """
    A dictionary of list values, each value being the composite filename for a season
    :param season:
    :return: list of current season clubs
    """

    shorthand = {
        '2019-20': '19_20',
        '2020-21': '20_21',
        '2021-22': '21_22',
        '2022-23': '22_23'}

    return shorthand[season]


def get_current_clubs(season):
    """
    A dictionary of list values, each value being the composite clubs for a season
    :param season:
    :return: list of current season clubs
    """

    all_clubs = {
        '2019-20': ['ars', 'avl', 'bha', 'bou', 'bur', 'che', 'cry', 'eve', 'lei', 'liv',
                    'mci', 'mun', 'new', 'nor', 'shu', 'sou', 'tot', 'wat', 'whu', 'wol'],
        '2020-21': ['ars', 'avl', 'bha', 'bur', 'che', 'cry', 'eve', 'ful', 'lee', 'lei',
                    'liv', 'mci', 'mun', 'new', 'shu', 'sou', 'tot', 'wba', 'whu', 'wol'],
        '2021-22': ['ars', 'avl', 'bha', 'brf', 'bur', 'che', 'cry', 'eve', 'lee', 'lei',
                    'liv', 'mci', 'mun', 'new', 'nor', 'sou', 'tot', 'wat', 'whu', 'wol'],
        '2022-23': ['ars', 'avl', 'bha', 'bou', 'brf', 'che', 'cry', 'eve', 'ful', 'lee',
                    'lei', 'liv', 'mci', 'mun', 'new', 'not', 'sou', 'tot', 'whu', 'wol']}

    return all_clubs[season]


def get_gameweek_dates(season):
    """
    Define the start and end date of each gameweek
    :param season:
    :return: dict of 2 key-list value pairs. Values are start and end dates
    """

    all_dates = {
        '2019-20': {'start_date': ['2020July23', '2020July18', '2020July14', '2020July10', '2020July07', '2020July03',
                                   '2020June26', '2020June23', '2020June13', '2020March02', '2020February25',
                                   '2020February20', '2020February03', '2020January30', '2020January20',
                                   '2020January13', '2020January03', '2020January01', '2019December28',
                                   '2019December23', '2019December17', '2019December10', '2019December06',
                                   '2019December02', '2019November26', '2019November11', '2019November04',
                                   '2019October28', '2019October22', '2019October07', '2019October01',
                                   '2019September23', '2019September17', '2019September02', '2019August26',
                                   '2019August20', '2019August12', '2019August09'],
                    'end_date': ['2020July26', '2020July22', '2020July17', '2020July13', '2020July09', '2020July06',
                                 '2020July02', '2020June25', '2020June22', '2020June12', '2020March01',
                                 '2020February24', '2020February19', '2020February02', '2020January29', '2020January19',
                                 '2020January12', '2020January02', '2019December31', '2019December27', '2019December22',
                                 '2019December16', '2019December09', '2019December05', '2019December01',
                                 '2019November25', '2019November10', '2019November03', '2019October27', '2019October21',
                                 '2019October06', '2019September30', '2019September22', '2019September16',
                                 '2019September01', '2019August25', '2019August19', '2019August11']},
        '2020-21': {'start_date': ['2021May22', '2021May18', '2021May14', '2021May07', '2021April30', '2021April23',
                                   '2021April16', '2021April09', '2021April02', '2021March19', '2021March12',
                                   '2021March05', '2021February26', '2021February19', '2021February12',
                                   '2021February05', '2021February02', '2021January29', '2021January26',
                                   '2021January15', '2021January12', '2021January01', '2020December28',
                                   '2020December25', '2020December18', '2020December15', '2020December11',
                                   '2020December04', '2020November27', '2020November20', '2020November06',
                                   '2020October29', '2020October23', '2020October16', '2020October02',
                                   '2020September25', '2020September18', '2020September12'],
                    'end_date': ['2021May23', '2021May21', '2021May17', '2021May13', '2021May06', '2021April29',
                                 '2021April22', '2021April15', '2021April08', '2021April01', '2021March18',
                                 '2021March11', '2021March04', '2021February25', '2021February18', '2021February11',
                                 '2021February04', '2021February01', '2021January28', '2021January25', '2021January14',
                                 '2021January11', '2020December31', '2020December27', '2020December24',
                                 '2020December17', '2020December14', '2020December10', '2020December03',
                                 '2020November26', '2020November19', '2020November05', '2020October29',
                                 '2020October22', '2020October15', '2020October01', '2020September24',
                                 '2020September17']},
        '2021-22': {'start_date': ['2022May20', '2022May13', '2022May06', '2022April29', '2022April22', '2022April15',
                                   '2022April08', '2022April01', '2022March18', '2022March11', '2022March04',
                                   '2022February25', '2022February18', '2022February11', '2022February08',
                                   '2022January21', '2022January14', '2022January01', '2021December28',
                                   '2021December25', '2021December17', '2021December14', '2021December10',
                                   '2021December03', '2021November30', '2021November26', '2021November19',
                                   '2021November05', '2021October29', '2021October22', '2021October15', '2021October01',
                                   '2021September24', '2021September17', '2021September10', '2021August27',
                                   '2021August20', '2021August13'],
                    'end_date': ['2022May22', '2022May19', '2022May12', '2022May05', '2022April28', '2022April21',
                                 '2022April14', '2022April07', '2022March31', '2022March17', '2022March10',
                                 '2022March03', '2022February24', '2022February17', '2022February10', '2022February07',
                                 '2022January20', '2022January13', '2021December31', '2021December27', '2021December24',
                                 '2021December16', '2021December13', '2021December09', '2021December02',
                                 '2021November29', '2021November25', '2021November18', '2021November04',
                                 '2021October28', '2021October21', '2021October14', '2021September30',
                                 '2021September23', '2021September16', '2021September09', '2021August26',
                                 '2021August19']},
        '2022-23': {'start_date': ['2023May26', '2023May19', '2023May12', '2023May05', '2023April28', '2023April25',
                                   '2023April21', '2023April14', '2023April07', '2023March31', '2023March17',
                                   '2023March10', '2023March03', '2023February24', '2023February17', '2023February10',
                                   '2023February03', '2023January20', '2023January13', '2023January02',
                                   '2022December30', '2022December26', '2022November11', '2022November04',
                                   '2022October28', '2022October21', '2022October18', '2022October14', '2022October07',
                                   '2022September30', '2022September16', '2022September09', '2022September02',
                                   '2022August30', '2022August26', '2022August19', '2022August12', '2022August05'],
                    'end_date': ['2023May28', '2023May25', '2023May18', '2023May11', '2023May04', '2023April27',
                                 '2023April24', '2023April20', '2023April13', '2023April06', '2023March30',
                                 '2023March16', '2023March09', '2023March02', '2023February23', '2023February16',
                                 '2023February09', '2023February02', '2023January19', '2023January12', '2023January01',
                                 '2022December29', '2022December25', '2022November10', '2022November03',
                                 '2022October27', '2022October20', '2022October17', '2022October13', '2022October06',
                                 '2022September29', '2022September15', '2022September08', '2022September01',
                                 '2022August29', '2022August25', '2022August18', '2022August11']}}

    return all_dates[season]
