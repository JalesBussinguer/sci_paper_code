import numpy as np
import geopandas as gpd
import pandas as pd
import os

from rasterstats import zonal_stats

form_florestal = gpd.read_file('D:/thesis_data/ROI/classes/form_florestal_30m_32723_buffer.GEOJSON')
form_savanica = gpd.read_file('D:/thesis_data/ROI/classes/form_savanica_30m_32723_buffer.GEOJSON')
form_campestre = gpd.read_file('D:/thesis_data/ROI/classes/form_campestre_30m_32723_buffer.GEOJSON')

images_path = 'D:/thesis_data/POL_DECOMP/rasters/'
image_list = os.listdir(images_path)

indices_list = ['DpRVI', 'PRVI', 'DPSVI', 'DPSVIm', 'RVI']

pol_list = ['entropy', 'alpha_angle']

for id, indice in enumerate(pol_list, start=1):

    df_florestal_stats = pd.DataFrame()
    df_savanica_stats = pd.DataFrame()
    df_campestre_stats = pd.DataFrame()

    for index, image in enumerate(image_list):

        date = image_list[index].split('_')[11].split('T')[0]

        florestal = zonal_stats(form_florestal, images_path + image, band=id, nodata=np.nan, stats=['median', 'percentile_25', 'percentile_75', 'std'])

        florestal_stats = pd.DataFrame(florestal)
        florestal_stats['date'] = pd.to_datetime(int(date), format='%Y%m%d')
        df_florestal_stats = pd.concat([florestal_stats, df_florestal_stats])

        print(f'{indice} - {date} florestal data collected')

        savanica = zonal_stats(form_savanica, images_path + image, band=id, nodata=np.nan, stats=['mean','median', 'percentile_25', 'percentile_75', 'std'])

        savanica_stats = pd.DataFrame(savanica)
        savanica_stats['date'] = pd.to_datetime(int(date), format='%Y%m%d')
        df_savanica_stats = pd.concat([savanica_stats, df_savanica_stats])

        print(f'{indice} - {date} savanica data collected!')

        campestre = zonal_stats(form_campestre, images_path + image, band=id, nodata=np.nan, stats=['mean','median', 'percentile_25', 'percentile_75', 'std'])

        campestre_stats = pd.DataFrame(campestre)
        campestre_stats['date'] = pd.to_datetime(int(date), format='%Y%m%d')
        df_campestre_stats = pd.concat([campestre_stats, df_campestre_stats])

        print(f'{indice} - {date} campestre data collected!')
        
    df_florestal_stats.to_csv('D:/thesis_data/POL_DECOMP/stats/' + 'florestal' + indice + '.csv', sep=',', index=False)
    print(f'{indice} florestal csv file saved!')

    df_savanica_stats.to_csv('D:/thesis_data/POL_DECOMP/stats/' + 'savanica' + indice + '.csv', sep=',', index=False)
    print(f'{indice} savanica csv file saved!')

    df_campestre_stats.to_csv('D:/thesis_data/POL_DECOMP/stats/' + 'campestre' + indice + '.csv', sep=',', index=False)
    print(f'{indice} campestre csv file saved!')