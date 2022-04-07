import numpy as np
import geopandas as gpd
import rasterio as rst
from rasterio.mask import mask
import pandas as pd
import os

pnb = gpd.read_file('D:/thesis_data/ROI/classes/form_campestre_10m_32723.GEOJSON')
pnb_geom = [geom for geom in pnb.geometry]

raster_path = 'D:/thesis_data/TOPOGRAPHY/slope_32723.tif'

with rst.open(raster_path) as raster:
    raster_clipped, raster_transform = mask(raster, pnb_geom, crop=True, nodata=-1)

    dem = raster_clipped[0]

df_dem = pd.DataFrame({'slope': dem.flatten()})
df_dem.dropna(inplace=True)

df_dem.to_csv('D:/thesis_data/TOPOGRAPHY/slope_fc_samples.csv', sep=',', index=False)
