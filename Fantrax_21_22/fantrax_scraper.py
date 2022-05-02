from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from datetime import datetime
import pandas as pd
from create_norm_scores_excel import create_wb, create_blank_sheet



capabilities = DesiredCapabilities().FIREFOX
capabilities["marionette"] = True
browser = webdriver.Firefox(executable_path="/usr/local/Cellar/geckodriver/0.27.0/bin/geckodriver")
wait = WebDriverWait(webdriver, 10)
startTime = datetime.now()


def fantrax_login():
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
    time.sleep(30)


def fantrax_logged_in():
    '''
    If already logged in. Try this as back up
    :return:
    '''
    browser.get('https://www.fantrax.com/login')


def obtain_results_table(link):
    '''
    Takes a player bio link and obtains the fantrax data table that is on that page/
    :param link: url for a fantrax player
    :return: df
    '''

    browser.get(link)
    time.sleep(10)
    # We want to go to Games(Fantasy) tab:
    try:
        nav_bar = browser.find_elements_by_class_name('tabs__item')
        browser.execute_script("arguments[0].click();", nav_bar[3])
    except IndexError:
        browser.refresh()
        time.sleep(10)
        nav_bar = browser.find_elements_by_class_name('tabs__item')
        browser.execute_script("arguments[0].click();", nav_bar[3])
    time.sleep(10)
    time.sleep(10)
    # Locate table and turn to dataframe.
    form_table = browser.find_elements_by_class_name('sticky-table')
    df = pd.read_html(form_table[0].get_attribute('outerHTML'))
    df = df[0].rename({"Unnamed: 0": "Date", "Unnamed: 1": "Team", "Unnamed: 2": "Opp",
                       "Unnamed: 3": "Score", "Unnamed: 4": "FPts", "Unnamed: 5": "Min",
                       "Unnamed: 6": "G", "Unnamed: 7": "KP", "Unnamed: 8": "AOG", "Unnamed: 9": "APKG",
                       "Unnamed: 10": "AT", "Unnamed: 11": "SOT", "Unnamed: 12": "TkW", "Unnamed: 13": "DIS",
                       "Unnamed: 14": "YC", "Unnamed: 15": "SYC", "Unnamed: 16": "RC",
                       "Unnamed: 17": "ACNC", "Unnamed: 18": "Int", "Unnamed: 19": "CLR", "Unnamed: 20": "CoS",
                       "Unnamed: 21": "BS", "Unnamed: 22": "AER", "Unnamed: 23": "BR",
                       "Unnamed: 24": "PKM", "Unnamed: 25": "OG", "Unnamed: 26": "GAD", "Unnamed: 27": "CS"}, axis=1)

    return df[["Date", "Team", "Opp", "Score", "FPts", "Min", "G"]]


def handle(club_links):
    '''
    Coordinates all actions

    :param args:
    :param options:
    :return:
    '''

    print('Uploading new Player Names data ...')

    fantrax_login()

    total_data = pd.DataFrame()

    for i in range(len(club_links)):
        data = pd.DataFrame(columns=['player', 'position', 'position_id',
                                     'date', 'team', 'opp', 'score', 'fpts', 'min', 'goals'])

        link = club_links.loc[i, "Link"]
        data[['date', 'team', 'opp', 'score', 'fpts', 'min', 'goals']] = obtain_results_table(link)
        data['player'] = club_links.loc[i, "Player"]
        data['position'] = club_links.loc[i, "Position"]
        data['position_id'] = club_links.loc[i, "Position ID"]

        print(data)

        total_data = total_data.append(data)

    return total_data


# ['ars', 'avl', 'brf', 'bha', 'bur', 'che', 'cry', 'eve', 'lee', 'lei',
# 'liv', 'mci', 'mun', 'new', 'nor', 'sou', 'tot', 'wat', 'whu', 'wol']
links = ['wol']

for file in links:
    club_links = pd.read_csv('links/' + file + '_links.csv')
    club_data = handle(club_links)
    club_data.to_csv('minute_data/' + file + '_minute_data.csv')
