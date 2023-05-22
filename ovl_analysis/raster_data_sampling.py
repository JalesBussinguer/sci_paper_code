import numpy as np
import geopandas as gpd
import rasterio as rst
from rasterio.mask import mask
import pandas as pd
import os

form_florestal = gpd.read_file('D:/thesis_data/ROI/classes/form_florestal_30m_32723.geojson')
florestal_geom = [geom for geom in form_florestal.geometry]

form_savanica = gpd.read_file('D:/thesis_data/ROI/classes/form_savanica_30m_32723.geojson')
savanica_geom = [geom for geom in form_savanica.geometry]

form_campestre = gpd.read_file('D:/thesis_data/ROI/classes/form_campestre_30m_32723.geojson')
campestre_geom = [geom for geom in form_campestre.geometry]

indices_path = os.listdir('D:/thesis_data/VEG_INDICES/raster')

for index, image in enumerate(indices_path):

    date = indices_path[index].split('T')[0]

    with rst.open('D:/thesis_data/VEG_INDICES/raster/' + str(image)) as raster:
        indices_clipped, indices_transform = mask(raster, florestal_geom, crop=True, nodata=np.nan)

        dprvi = indices_clipped[0]
        prvi = indices_clipped[1]
        dpsvi = indices_clipped[2]
        dpsvim = indices_clipped[3]
        rvi = indices_clipped[4]

    df_florestal = pd.DataFrame({'DpRVI': dprvi.flatten(), 'PRVI': prvi.flatten(), 'DPSVI': dpsvi.flatten(), 'DPSVIm': dpsvim.flatten(), 'RVI': rvi.flatten()})
    df_florestal.dropna(inplace=True)

    df_florestal.to_csv('D:/thesis_data/VEG_INDICES/samples/ff_dists/' + 'florestal_' + date + '_distribution' + '.csv', sep=',')

    print(f'Florestal data of {date} collected!')

    with rst.open('D:/thesis_data/VEG_INDICES/raster/' + str(image)) as raster:
        indices_clipped, indices_transform = mask(raster, savanica_geom, crop=True, nodata=np.nan)

        dprvi = indices_clipped[0]
        prvi = indices_clipped[1]
        dpsvi = indices_clipped[2]
        dpsvim = indices_clipped[3]
        rvi = indices_clipped[4]

    df_savanica = pd.DataFrame({'DpRVI': dprvi.flatten(), 'PRVI': prvi.flatten(), 'DPSVI': dpsvi.flatten(), 'DPSVIm': dpsvim.flatten(), 'RVI': rvi.flatten()})
    df_savanica.dropna(inplace=True)

    df_savanica.to_csv('D:/thesis_data/VEG_INDICES/samples/fs_dists/' + 'savanica_' + date + '_distribution' + '.csv', sep=',')

    print(f'Savanica data of {date} collected!')

    with rst.open('D:/thesis_data/VEG_INDICES/raster/' + str(image)) as raster:
        indices_clipped, indices_transform = mask(raster, campestre_geom, crop=True, nodata=np.nan)

        dprvi = indices_clipped[0]
        prvi = indices_clipped[1]
        dpsvi = indices_clipped[2]
        dpsvim = indices_clipped[3]
        rvi = indices_clipped[4]

    df_campestre = pd.DataFrame({'DpRVI': dprvi.flatten(), 'PRVI': prvi.flatten(), 'DPSVI': dpsvi.flatten(), 'DPSVIm': dpsvim.flatten(), 'RVI': rvi.flatten()})
    df_campestre.dropna(inplace=True)

    df_campestre.to_csv('D:/thesis_data/VEG_INDICES/samples/fc_dists/' + 'campestre_' + date + '_distribution' + '.csv', sep=',')

    print(f'Campestre data of {date} collected!')










#     savanica = point_query(form_savanica, 'D:/thesis_data/VEG_INDICES/' + str(image), band=1, nodata=np.nan)

#     df_savanica = pd.DataFrame({'DpRVI': savanica})
#     df_savanica.dropna(inplace=True)
#     df_savanica.to_csv('D:/thesis_data/VEG_INDICES/samples/DpRVI/' + 'savanica' + date + 'distribution' + '.csv', sep=',')

#     savanica_median = np.median(df_savanica['DpRVI'])
#     savanica_mean = np.mean(df_savanica['DpRVI'])
#     savanica_std = np.std(df_savanica['DpRVI'])

#     savanica_stats = pd.DataFrame({'date': date, 'median': savanica_median, 'mean': savanica_mean, 'std': savanica_std}, index=[0])
#     savanica_df_stats.append(savanica_stats)

#     print(f'Savanica data of {date} collected!')


#     campestre = point_query(form_campestre, 'D:/thesis_data/VEG_INDICES/' + str(image), band=1, nodata=np.nan)

#     df_campestre = pd.DataFrame({'DpRVI': campestre})
#     df_campestre.dropna(inplace=True)
#     df_campestre.to_csv('D:/thesis_data/VEG_INDICES/samples/DpRVI/' + 'campestre' + date + 'distribution' + '.csv', sep=',')

#     campestre_median = np.median(df_campestre['DpRVI'])
#     campestre_mean = np.mean(df_campestre['DpRVI'])
#     campestre_std = np.std(df_campestre['DpRVI'])

#     campestre_stats = pd.DataFrame({'date': date, 'median': campestre_median, 'mean': campestre_mean, 'std': campestre_std}, index=[0])
#     campestre_df_stats.append(campestre_stats)

#     print(f'Campestre data of {date} collected!')

# florestal_df_stats.to_csv('D:/thesis_data/VEG_INDICES/samples/DpRVI/' + 'florestal' + date + 'stats' + '.csv', sep=',')
# savanica_df_stats.to_csv('D:/thesis_data/VEG_INDICES/samples/DpRVI/' + 'savanica' + date + 'stats' + '.csv', sep=',')
# campestre_df_stats.to_csv('D:/thesis_data/VEG_INDICES/samples/DpRVI/' + 'campestre' + date + 'stats' + '.csv', sep=',')

# print(f'DpRVI stats collected!')