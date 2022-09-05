import pandas as pd
import numpy as np


def get_summary_agg(df):

    active_df = df[(df['Start'] == 1) & (df['Predict'] >= 12)]
    unique_active_df = pd.pivot_table(active_df, index='Name', values='Start', aggfunc=np.sum)
    df.drop(columns=['Unnamed: 0', 'Unnamed: 1'], inplace=True)
    unique_names = df['Name'].unique()
    df.reset_index(inplace=True)
    summary_df = pd.pivot_table(df, index='Name', values=['NormScore', 'Return', 'Start'],
                                aggfunc={'NormScore': np.mean, 'Return': np.sum, 'Start': np.sum})
    summary_df = summary_df.merge(unique_active_df, on='Name', how='left')
    summary_df.rename(columns={'Start_x': 'Starts', 'Start_y': 'Active Starts'}, inplace=True)
    summary_df['NormScore'] = np.round(summary_df['NormScore'], 2)
    summary_df['% Active'] = np.round(summary_df['Active Starts']/summary_df['Starts']*100, 2)
    summary_df.replace({np.nan: 0}, inplace=True)

    print(summary_df)

    return summary_df


clubs = ['ars', 'avl', 'brf', 'bha', 'bur', 'che', 'cry', 'eve', 'lee', 'lei',
         'liv', 'mci', 'mun', 'new', 'nor', 'sou', 'tot', 'wat', 'whu', 'wol']


season_summary_df = pd.DataFrame()
for club in clubs:
    df = pd.read_excel(io='FantraxXIs2021_22.xlsx', sheet_name=club, skiprows=5)
    club_season_summary_df = get_summary_agg(df)
    season_summary_df = pd.concat([season_summary_df, club_season_summary_df], axis=0)
    season_summary_df.to_csv('SummaryStats2021_22.csv')
