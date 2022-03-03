import numpy as np
import geopandas as gpd
import pandas as pd
import os

from rasterstats import zonal_stats

form_florestal = gpd.read_file('D:/thesis_data/ROI/classes/form_florestal_10m_32723.GEOJSON')
form_savanica = gpd.read_file('D:/thesis_data/ROI/classes/form_savanica_10m_32723.GEOJSON')
form_campestre = gpd.read_file('D:/thesis_data/ROI/classes/form_campestre_10m_32723.GEOJSON')

indices_path = os.listdir('D:/thesis_data/VEG_INDICES/raster/')

indices_list = ['DpRVI', 'PRVI', 'DPSVI', 'DPSVIm', 'RVI']

df_florestal_stats = pd.DataFrame()
df_savanica_stats = pd.DataFrame()
df_campestre_stats = pd.DataFrame()

for id, indice in enumerate(indices_list, start=1):

    for index, image in enumerate(indices_path):

        date = indices_path[index].split('.')[0]

        florestal = zonal_stats(form_florestal, 'D:/thesis_data/VEG_INDICES/raster/' + image, band=id, nodata=np.nan, stats=['median', 'mean', 'std'])

        florestal_stats = pd.DataFrame(florestal)
        florestal_stats['date'] = date
        df_florestal_stats = pd.concat([florestal_stats, df_florestal_stats], ignore_index=True)

        print(f'{indice} - {date} florestal data collected')

    df_florestal_stats.to_csv('D:/thesis_data/VEG_INDICES/stats/' + 'florestal' + indice + '.csv', sep=',')

    print(f'{indice} florestal csv file saved!')

    for index, image in enumerate(indices_path):

        date = indices_path[index].split('.')[0]

        savanica = zonal_stats(form_savanica, 'D:/thesis_data/VEG_INDICES/raster/' + image, band=id, nodata=np.nan, stats=['median', 'mean', 'std'])

        savanica_stats = pd.DataFrame(savanica)
        savanica_stats['date'] = date
        df_savanica_stats = pd.concat([savanica_stats, df_savanica_stats], ignore_index=True)

        print(f'{indice} - {date} savanica data collected!')
    
    df_savanica_stats.to_csv('D:/thesis_data/VEG_INDICES/stats/'+ 'savanica' + indice + '.csv', sep=',')

    print(f'{indice} savanica csv file saved!')

    for index, image in enumerate(indices_path):

        date = indices_path[index].split('.')[0]

        campestre = zonal_stats(form_campestre, 'D:/thesis_data/VEG_INDICES/raster/' + image, band=id, nodata=np.nan, stats=['median', 'mean', 'std'])

        campestre_stats = pd.DataFrame(campestre)
        campestre_stats['date'] = date
        df_campestre_stats = pd.concat([campestre_stats, df_campestre_stats], ignore_index=True)

        print(f'{indice} - {date} campestre data collected!')
    
    df_campestre_stats.to_csv('D:/thesis_data/VEG_INDICES/stats/'+ 'campestre' + indice + '.csv', sep=',')

    print(f'{indice} campestre csv file saved!')