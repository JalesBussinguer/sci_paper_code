import numpy as np
import geopandas as gpd
import rasterio as rst
from rasterio.mask import mask
import pandas as pd
import os


form_florestal = gpd.read_file('D:/thesis_data/ROI/sampling/sample_grid_mapbiomas/FF_mapbiomas_50_sampling_grids_20m_32723.GEOJSON')
florestal_geom = [geom for geom in form_florestal.geometry]

form_savanica = gpd.read_file('D:/thesis_data/ROI/sampling/sample_grid_mapbiomas/FS_mapbiomas_50_sampling_grids_20m_32723.GEOJSON')
savanica_geom = [geom for geom in form_savanica.geometry]

form_campestre = gpd.read_file('D:/thesis_data/ROI/sampling/sample_grid_mapbiomas/FC_mapbiomas_50_sampling_grids_20m_32723.GEOJSON')
campestre_geom = [geom for geom in form_campestre.geometry]

raster_path = 'D:/thesis_data/VEG_INDICES/dpsvi_parameters/raster/'

indices_list = os.listdir(raster_path)


# Gallery Forests
for index, image in enumerate(indices_list):

    date = indices_list[index].split('_')[2].split('.')[0]

    df_ff = pd.DataFrame()

    for (i, _) in enumerate(florestal_geom):

        with rst.open(raster_path + str(image)) as raster:
            indices_clipped, indices_transform = mask(raster, [florestal_geom[i]], crop=True, nodata=np.nan)

            dpsvi = indices_clipped[2]

        df_ff[f'dpsvi_patch_{i}'] = pd.Series(dpsvi.flatten())
        df_ff.dropna(inplace=True)

    df_ff.to_csv('D:/thesis_data/VEG_INDICES/dpsvi_parameters/samples/' + 'FF_' + date + '_20m_patches' + '.csv', sep=',', index=False)

    print(f'Forest data patches of {date} collected!')


# Savanna
for index, image in enumerate(indices_list):

    date = indices_list[index].split('_')[2].split('.')[0]

    df_fs = pd.DataFrame()

    for (i, _) in enumerate(savanica_geom):

        with rst.open(raster_path + str(image)) as raster:
            indices_clipped, indices_transform = mask(raster, [savanica_geom[i]], crop=True, nodata=np.nan)


            dpsvi = indices_clipped[2]

        df_fs[f'dpsvi_patch_{i}'] = pd.Series(dpsvi.flatten())
        df_fs.dropna(inplace=True)

    df_fs.to_csv('D:/thesis_data/VEG_INDICES/dpsvi_parameters/samples/' + 'FS_' + date + '_20m_patches' + '.csv', sep=',', index=False)

    print(f'Savanna data patches of {date} collected!')


# Grasslands
for index, image in enumerate(indices_list):

    date = indices_list[index].split('_')[2].split('.')[0]

    df_fc = pd.DataFrame()

    for (i, _) in enumerate(campestre_geom):

        with rst.open(raster_path + str(image)) as raster:
            indices_clipped, indices_transform = mask(raster, [campestre_geom[i]], crop=True, nodata=np.nan)

            dpsvi = indices_clipped[2]
        
        df_fc[f'dpsvi_patch_{i}'] = pd.Series(dpsvi.flatten())
        df_fc.dropna(inplace=True)

    df_fc.to_csv('D:/thesis_data/VEG_INDICES/dpsvi_parameters/samples/' + 'FC_' + date + '_20m_patches' + '.csv', sep=',', index=False)
    print(f'Grasslands data patches of {date} collected!')