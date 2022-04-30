import numpy as np
import geopandas as gpd
import rasterio as rst
from rasterio.mask import mask
import pandas as pd
import os

# from rasterstats import point_query

form_florestal = gpd.read_file('D:/thesis_data/ROI/sampling/FF_50_sampling_grids_10m_32723.GEOJSON')
florestal_geom = [geom for geom in form_florestal.geometry]

form_savanica = gpd.read_file('D:/thesis_data/ROI/sampling/FS_50_sampling_grids_10m_32723.GEOJSON')
savanica_geom = [geom for geom in form_savanica.geometry]

form_campestre = gpd.read_file('D:/thesis_data/ROI/sampling/FC_50_sampling_grids_10m_32723.GEOJSON')
campestre_geom = [geom for geom in form_campestre.geometry]

indices_path = os.listdir('D:/thesis_data/VEG_INDICES/raster')

for index, image in enumerate(indices_path):

    date = indices_path[index].split('T')[0]

    df_ff = pd.DataFrame()
    # df_ff_prvi = pd.DataFrame()
    # df_ff_dpsvi = pd.DataFrame()
    # df_ff_dpsvim = pd.DataFrame()
    # df_ff_rvi = pd.DataFrame()

    for (i, _) in enumerate(florestal_geom):

        with rst.open('D:/thesis_data/VEG_INDICES/raster/' + str(image)) as raster:
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
        # df_ff_prvi.dropna(inplace=True)
        # df_ff_dpsvi.dropna(inplace=True)
        # df_ff_dpsvim.dropna(inplace=True)
        # df_ff_rvi.dropna(inplace=True)

    df_ff.to_csv('D:/thesis_data/VEG_INDICES/samples/stratified/florestal/' + 'FF_' + date + '_patches' + '.csv', sep=',', index=False)
    # df_ff_prvi.to_csv('D:/thesis_data/VEG_INDICES/samples/stratified/' + 'PRVI_ff_' + date + '_patches' + '.csv', sep=',', index=False)
    # df_ff_dpsvi.to_csv('D:/thesis_data/VEG_INDICES/samples/stratified/' + 'DPSVI_ff_' + date + '_patches' + '.csv', sep=',', index=False)
    # df_ff_dpsvim.to_csv('D:/thesis_data/VEG_INDICES/samples/stratified/' + 'DPSVIm_ff_' + date + '_patches' + '.csv', sep=',', index=False)
    # df_ff_rvi.to_csv('D:/thesis_data/VEG_INDICES/samples/stratified/' + 'RVI_ff_' + date + '_patches' + '.csv', sep=',', index=False)

    print(f'Forest data patches of {date} collected!')

for index, image in enumerate(indices_path):

    date = indices_path[index].split('T')[0]

    df_fs = pd.DataFrame()
    # df_ff_prvi = pd.DataFrame()
    # df_ff_dpsvi = pd.DataFrame()
    # df_ff_dpsvim = pd.DataFrame()
    # df_ff_rvi = pd.DataFrame()

    for (i, _) in enumerate(savanica_geom):

        with rst.open('D:/thesis_data/VEG_INDICES/raster/' + str(image)) as raster:
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
        # df_ff_prvi.dropna(inplace=True)
        # df_ff_dpsvi.dropna(inplace=True)
        # df_ff_dpsvim.dropna(inplace=True)
        # df_ff_rvi.dropna(inplace=True)

    df_fs.to_csv('D:/thesis_data/VEG_INDICES/samples/stratified/savanica/' + 'FS_' + date + '_patches' + '.csv', sep=',', index=False)
    # df_ff_prvi.to_csv('D:/thesis_data/VEG_INDICES/samples/stratified/' + 'PRVI_ff_' + date + '_patches' + '.csv', sep=',', index=False)
    # df_ff_dpsvi.to_csv('D:/thesis_data/VEG_INDICES/samples/stratified/' + 'DPSVI_ff_' + date + '_patches' + '.csv', sep=',', index=False)
    # df_ff_dpsvim.to_csv('D:/thesis_data/VEG_INDICES/samples/stratified/' + 'DPSVIm_ff_' + date + '_patches' + '.csv', sep=',', index=False)
    # df_ff_rvi.to_csv('D:/thesis_data/VEG_INDICES/samples/stratified/' + 'RVI_ff_' + date + '_patches' + '.csv', sep=',', index=False)

    print(f'Savanna data patches of {date} collected!')

for index, image in enumerate(indices_path):

    date = indices_path[index].split('T')[0]

    df_fc = pd.DataFrame()
    # df_ff_prvi = pd.DataFrame()
    # df_ff_dpsvi = pd.DataFrame()
    # df_ff_dpsvim = pd.DataFrame()
    # df_ff_rvi = pd.DataFrame()

    for (i, _) in enumerate(campestre_geom):

        with rst.open('D:/thesis_data/VEG_INDICES/raster/' + str(image)) as raster:
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
        # df_ff_prvi.dropna(inplace=True)
        # df_ff_dpsvi.dropna(inplace=True)
        # df_ff_dpsvim.dropna(inplace=True)
        # df_ff_rvi.dropna(inplace=True)

    df_fc.to_csv('D:/thesis_data/VEG_INDICES/samples/stratified/campestre/' + 'FC_' + date + '_patches' + '.csv', sep=',', index=False)
    # df_ff_prvi.to_csv('D:/thesis_data/VEG_INDICES/samples/stratified/' + 'PRVI_ff_' + date + '_patches' + '.csv', sep=',', index=False)
    # df_ff_dpsvi.to_csv('D:/thesis_data/VEG_INDICES/samples/stratified/' + 'DPSVI_ff_' + date + '_patches' + '.csv', sep=',', index=False)
    # df_ff_dpsvim.to_csv('D:/thesis_data/VEG_INDICES/samples/stratified/' + 'DPSVIm_ff_' + date + '_patches' + '.csv', sep=',', index=False)
    # df_ff_rvi.to_csv('D:/thesis_data/VEG_INDICES/samples/stratified/' + 'RVI_ff_' + date + '_patches' + '.csv', sep=',', index=False)

    print(f'Grasslands data patches of {date} collected!')
