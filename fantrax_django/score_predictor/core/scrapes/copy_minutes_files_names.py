import pandas as pd
import numpy as np
import os

path_to_folder = os.path.join(os.getcwd(), 'core', 'scrapes', 'minutes')


transfermarkt_names = []
for filename in os.listdir(path_to_folder):
    stringed_name = str(filename)
    transfermarkt_names.append(stringed_name[:-4])

transfermarkt_names = pd.Series(transfermarkt_names).sort_values()
