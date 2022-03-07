import numpy as np
import geopandas as gpd
import pandas as pd
import os

from rasterstats import point_query

water_mask = gpd.read_file('D:/thesis_data/ROI/classes/form_florestal_10m_32723.GEOJSON')

indices = os.listdir('D:/thesis_data/VEG_INDICES/dprvi_parameters/')

for index, image in enumerate(indices):

    date = indices[index].split('.')[0]

    dprvi = point_query(water_mask, 'D:/thesis_data/VEG_INDICES/dprvi_parameters/' + str(image), band=1, nodata=np.nan)
    dprvi = np.array(dprvi)
    print(f'DpRVI data collected!')

    dop = point_query(water_mask, 'D:/thesis_data/VEG_INDICES/dprvi_parameters/' + str(image), band=2, nodata=np.nan)
    dop = np.array(dop)
    print(f'DOP data collected!')

    lambda1 = point_query(water_mask, 'D:/thesis_data/VEG_INDICES/dprvi_parameters/' + str(image), band=3, nodata=np.nan)
    lambda1 = np.array(lambda1)
    print(f'Lambda1 data collected!')

    lambda2 = point_query(water_mask, 'D:/thesis_data/VEG_INDICES/dprvi_parameters/' + str(image), band=4, nodata=np.nan)
    lambda2 = np.array(lambda2)
    print(f'Lambda2 data collected!')

    beta = point_query(water_mask, 'D:/thesis_data/VEG_INDICES/dprvi_parameters/' + str(image), band=5, nodata=np.nan)
    beta = np.array(beta)
    print(f'Beta data collected!')

    df_water = pd.DataFrame({'DpRVI': dprvi.flatten(), 'DOP': dop.flatten(), 'Lambda1': lambda1.flatten(), 'Lambda2': lambda2.flatten(), 'Beta': beta.flatten()})
    df_water.dropna(inplace=True)

    df_water.to_csv('D:/thesis_data/VEG_INDICES/samples/water/' + 'florestal_' + date + '_samples' + '.csv', sep=',', index=False)

    print(f'Florestal data of {date} collected!')