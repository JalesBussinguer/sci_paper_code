import argparse
import numpy as np
import rasterio as rst
from rasterio.mask import mask

import geopandas as gpd

import os

import time
from functools import wraps

def _get_args():

    '''
    Input parameters parser
    '''

    parser = argparse.ArgumentParser()

    parser.add_argument('-j', '--json',
    help='The input json file cotaining the preprocessing settings',
    type=str)

    args = parser.parse_args()

    return args

def timing(func): # Processing time decorator
    @wraps(func)
    def processing_time(*args, **kwargs):
        t1 = time.time()
        result = func(*args, **kwargs)
        t2 = time.time()
        print(f'@timing: {func.__name__} took {t2-t1} seconds')
        return result
    return processing_time

@timing
def dpdd_index(vv, vh):

    dpdd = (vv + vh) / 1.4142

    return dpdd.astype(np.float32)

@timing
def cr_index(vv, vh):

    cr = vv / vh

    return cr.astype(np.float32)


@timing
def dpsvim_index(vv, vh):

    """
    DPSVIm - Modified Dual-Pol SAR Vegetation Index

    Args:

    VV (array) = Vertical-Vertical polarization \n
    VH (array) = Vertical-Horizontal polarization
    
    Returns:
        DPSVIm (array)
    """
    
    dpsvim = (np.power(vv, 2) + (vv * vh)) / (1.4142)

    return dpsvim.astype(np.float32)


@timing
def _main(settings):

    roi = gpd.read_file(settings['roi_path'])

    geometries = [geom for geom in roi.geometry]

    for i, _ in enumerate(os.listdir(settings['grd_image'])):

        indices_list = []

        grd_image = os.listdir(settings['grd_image'])[i]

        if grd_image.endswith('.tif'):

            date = grd_image.split('_')[1].split('T')[0]

            grd_file = settings['grd_image'] + '/' + grd_image

            # SAR GRD image
            with rst.open(grd_file) as grd:

                grd_image, grd_transform = mask(grd, geometries, crop=True, nodata=np.nan)

                vh = grd_image[0]
                vv = grd_image[1]
               

        # DPDD
        dpdd = dpdd_index(vv, vh)
        indices_list.append(dpdd)
        
        # CR
        cr = cr_index(vv, vh)
        indices_list.append(cr)

        # DPSVIm
        dpsvim = dpsvim_index(vv, vh)
        indices_list.append(dpsvim)


        out_meta = grd.meta

        out_meta.update({
                        "driver": "GTiff",
                        "height": dpdd.shape[0],
                        "width": dpdd.shape[1],
                        "transform": grd_transform,
                        "count": len(indices_list)
                        })

        with rst.open(settings['indices_outpath'] + '/' + 'dpsvim_parameters_' + date + '.tif', "w", **out_meta) as dest:
            for id, indice in enumerate(indices_list, start=1):
                dest.write(indice, id)

if __name__ == "__main__":

    import json

    args = _get_args()

    file = open(args.json)

    params = json.load(file)

    _main(params)