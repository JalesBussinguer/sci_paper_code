import numpy as np
import geopandas as gpd
import pandas as pd
import os

import rasterio as rst
from rasterio.mask import mask

bnp = gpd.read_file('D:/thesis_data/ROI/ROI_PNB_32723.geojson')
bnp = [geom for geom in bnp.geometry]

images_path = 'D:/thesis_data/SAR/preprocessed/GRD/'
image_list = os.listdir(images_path)

id = 1

vv_max_stats = []
dates = []

for index, image in enumerate(image_list):

    date = image_list[index].split('_')[1].split('T')[0]

    with rst.open(images_path + image) as raster:
        image, _ = mask(raster, bnp, invert=True, nodata=np.nan)

        vv = image[0]
        vh = image[1]

    
    vv_max = np.nanmax(vv)

    #idpdd = ((vv_max - vv) + vh) / 1.4142

    #vddpi = (vv + vh) / vv

    vv_max_stats.append(vv_max)

    dates.append(pd.to_datetime(int(date), format='%Y%m%d'))

    print(f'{date} VV max collected')

df_vv_max_stats = pd.DataFrame({'date': dates, 'vv_max': vv_max_stats})

df_vv_max_stats.to_csv('D:/thesis_data/VEG_INDICES/VV_max.csv', sep=',', index=False)
print('VV max csv file saved!')
