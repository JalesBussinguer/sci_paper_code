import numpy as np
import geopandas as gpd
import pandas as pd
import os

from rasterstats import point_query

florestal_df_stats = pd.DataFrame()
savanica_df_stats = pd.DataFrame()
campestre_df_stats = pd.DataFrame()

form_florestal = gpd.read_file('D:/thesis_data/ROI/classes/form_florestal_10m_32723.GEOJSON')
form_savanica = gpd.read_file('D:/thesis_data/ROI/classes/form_savanica_10m_32723.GEOJSON')
form_campestre = gpd.read_file('D:/thesis_data/ROI/classes/form_campestre_10m_32723.GEOJSON')

indices = os.listdir('D:/thesis_data/VEG_INDICES')

for index, image in enumerate(indices):

    date = indices[index].split('.')[0]

    florestal = point_query(form_florestal, 'D:/thesis_data/VEG_INDICES/' + str(image), band=1, nodata=np.nan)

    df_florestal = pd.DataFrame({'DpRVI': florestal})
    df_florestal.dropna(inplace=True)
    df_florestal.to_csv('D:/thesis_data/VEG_INDICES/samples/DpRVI/' + 'florestal' + date + 'distribution' + '.csv', sep=',')

    florestal_median = np.median(df_florestal['DpRVI'])
    florestal_mean = np.mean(df_florestal['DpRVI'])
    florestal_std = np.std(df_florestal['DpRVI'])

    florestal_stats = pd.DataFrame({'date': date, 'median': florestal_median, 'mean': florestal_mean, 'std': florestal_std}, index=[0])
    florestal_df_stats.append(florestal_stats)

    print(f'Florestal data of {date} collected!')


    savanica = point_query(form_savanica, 'D:/thesis_data/VEG_INDICES/' + str(image), band=1, nodata=np.nan)

    df_savanica = pd.DataFrame({'DpRVI': savanica})
    df_savanica.dropna(inplace=True)
    df_savanica.to_csv('D:/thesis_data/VEG_INDICES/samples/DpRVI/' + 'savanica' + date + 'distribution' + '.csv', sep=',')

    savanica_median = np.median(df_savanica['DpRVI'])
    savanica_mean = np.mean(df_savanica['DpRVI'])
    savanica_std = np.std(df_savanica['DpRVI'])

    savanica_stats = pd.DataFrame({'date': date, 'median': savanica_median, 'mean': savanica_mean, 'std': savanica_std}, index=[0])
    savanica_df_stats.append(savanica_stats)

    print(f'Savanica data of {date} collected!')


    campestre = point_query(form_campestre, 'D:/thesis_data/VEG_INDICES/' + str(image), band=1, nodata=np.nan)

    df_campestre = pd.DataFrame({'DpRVI': campestre})
    df_campestre.dropna(inplace=True)
    df_campestre.to_csv('D:/thesis_data/VEG_INDICES/samples/DpRVI/' + 'campestre' + date + 'distribution' + '.csv', sep=',')

    campestre_median = np.median(df_campestre['DpRVI'])
    campestre_mean = np.mean(df_campestre['DpRVI'])
    campestre_std = np.std(df_campestre['DpRVI'])

    campestre_stats = pd.DataFrame({'date': date, 'median': campestre_median, 'mean': campestre_mean, 'std': campestre_std}, index=[0])
    campestre_df_stats.append(campestre_stats)

    print(f'Campestre data of {date} collected!')

florestal_df_stats.to_csv('D:/thesis_data/VEG_INDICES/samples/DpRVI/' + 'florestal' + date + 'stats' + '.csv', sep=',')
savanica_df_stats.to_csv('D:/thesis_data/VEG_INDICES/samples/DpRVI/' + 'savanica' + date + 'stats' + '.csv', sep=',')
campestre_df_stats.to_csv('D:/thesis_data/VEG_INDICES/samples/DpRVI/' + 'campestre' + date + 'stats' + '.csv', sep=',')

print(f'DpRVI stats collected!')