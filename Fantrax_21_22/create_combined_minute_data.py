import pandas as pd

clubs = ['ars', 'avl', 'brf', 'bha', 'bur', 'che', 'cry', 'eve', 'lee', 'lei', 'liv', 'mci', 'mun', 'new', 'nor',
         'sou', 'tot', 'wat', 'whu', 'wol']

pre_conditions = pd.read_csv('initial_conditions_last_year.csv')

combined_minute_data = pd.DataFrame({})

for club in clubs:
    club_minute_data = pd.read_csv('minute_data/' + club + '_minute_data.csv')
    combined_minute_data = pd.concat([combined_minute_data, club_minute_data], ignore_index=True)

combined_minute_data.to_csv('minute_data/combined_minute_data_2021_22.csv')
