import numpy as np
import geopandas as gpd
import rasterio as rst
from rasterio.mask import mask
import pandas as pd
import os


form_florestal = gpd.read_file('D:/thesis_data/ROI/sampling/sample_grid_mapbiomas/FF_mapbiomas_250_sampling_grids_100x100m_32723.GEOJSON')
florestal_geom = [geom for geom in form_florestal.geometry]

form_savanica = gpd.read_file('D:/thesis_data/ROI/sampling/sample_grid_mapbiomas/FS_mapbiomas_250_sampling_grids_100x100m_32723.GEOJSON')
savanica_geom = [geom for geom in form_savanica.geometry]

form_campestre = gpd.read_file('D:/thesis_data/ROI/sampling/sample_grid_mapbiomas/FC_mapbiomas_250_sampling_grids_100x100m_32723.GEOJSON')
campestre_geom = [geom for geom in form_campestre.geometry]

raster_path = 'D:/thesis_data/VEG_INDICES/raster/'

indices_list = os.listdir(raster_path)


# Gallery Forests
for index, image in enumerate(indices_list):

    date = indices_list[index].split('T')[0]

    df_ff = pd.DataFrame()

    for (i, _) in enumerate(florestal_geom):

        with rst.open(raster_path + str(image)) as raster:
            indices_clipped, indices_transform = mask(raster, [florestal_geom[i]], crop=True, nodata=np.nan)

            dprvi = indices_clipped[0]
            prvi = indices_clipped[1]
            dpsvi = indices_clipped[2]
            dpsvim = indices_clipped[3]
            rvi = indices_clipped[4]
        
        df_ff[f'dprvi_patch_{i}'] = pd.Series(dprvi.flatten())
        df_ff[f'prvi_patch_{i}'] = pd.Series(prvi.flatten())
        df_ff[f'dpsvi_patch_{i}'] = pd.Series(dpsvi.flatten())
        df_ff[f'dpsvim_patch_{i}'] = pd.Series(dpsvim.flatten())
        df_ff[f'rvi_patch_{i}'] = pd.Series(rvi.flatten())

        df_ff.dropna(inplace=True)

    df_ff.to_csv('D:/thesis_data/VEG_INDICES/samples/stratified/florestal/100m/' + 'FF_' + date + '_100x100m_patches' + '.csv', sep=',', index=False)

    print(f'Forest data patches of {date} collected!')


# Savanna
for index, image in enumerate(indices_list):

    date = indices_list[index].split('T')[0]

    df_fs = pd.DataFrame()

    for (i, _) in enumerate(savanica_geom):

        with rst.open(raster_path + str(image)) as raster:
            indices_clipped, indices_transform = mask(raster, [savanica_geom[i]], crop=True, nodata=np.nan)

            dprvi = indices_clipped[0]
            prvi = indices_clipped[1]
            dpsvi = indices_clipped[2]
            dpsvim = indices_clipped[3]
            rvi = indices_clipped[4]
        
        df_fs[f'dprvi_patch_{i}'] = pd.Series(dprvi.flatten())
        df_fs[f'prvi_patch_{i}'] = pd.Series(prvi.flatten())
        df_fs[f'dpsvi_patch_{i}'] = pd.Series(dpsvi.flatten())
        df_fs[f'dpsvim_patch_{i}'] = pd.Series(dpsvim.flatten())
        df_fs[f'rvi_patch_{i}'] = pd.Series(rvi.flatten())

        df_fs.dropna(inplace=True)

    df_fs.to_csv('D:/thesis_data/VEG_INDICES/samples/stratified/savanica/100m/' + 'FS_' + date + '_100x100m_patches' + '.csv', sep=',', index=False)

    print(f'Savanna data patches of {date} collected!')


# Grasslands
for index, image in enumerate(indices_list):

    date = indices_list[index].split('T')[0]

    df_fc = pd.DataFrame()

    for (i, _) in enumerate(campestre_geom):

        with rst.open(raster_path + str(image)) as raster:
            indices_clipped, indices_transform = mask(raster, [campestre_geom[i]], crop=True, nodata=np.nan)

            dprvi = indices_clipped[0]
            prvi = indices_clipped[1]
            dpsvi = indices_clipped[2]
            dpsvim = indices_clipped[3]
            rvi = indices_clipped[4]
        
        df_fc[f'dprvi_patch_{i}'] = pd.Series(dprvi.flatten())
        df_fc[f'prvi_patch_{i}'] = pd.Series(prvi.flatten())
        df_fc[f'dpsvi_patch_{i}'] = pd.Series(dpsvi.flatten())
        df_fc[f'dpsvim_patch_{i}'] = pd.Series(dpsvim.flatten())
        df_fc[f'rvi_patch_{i}'] = pd.Series(rvi.flatten())

        df_fc.dropna(inplace=True)

    df_fc.to_csv('D:/thesis_data/VEG_INDICES/samples/stratified/campestre/100m/' + 'FC_' + date + '_100x100m_patches' + '.csv', sep=',', index=False)
    print(f'Grasslands data patches of {date} collected!')
