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

# Processing time decorator
def timing(func): 
    @wraps(func)
    def processing_time(*args, **kwargs):
        t1 = time.time()
        result = func(*args, **kwargs)
        t2 = time.time()
        print(f'@timing: {func.__name__} took {t2-t1} seconds')
        return result
    return processing_time

# Tools
def conv2d(matrix, window):

    # Convolution operator

    filtered = np.zeros(matrix.shape)
    wspad = int(window.shape[0]/2)

    s = window.shape + tuple(np.subtract(matrix.shape, window.shape) + 1)

    # convolution type
    strd = np.lib.stride_tricks.as_strided
    subM = strd(matrix, shape=s, strides = matrix.strides * 2)

    filtered_data = np.einsum('ij,ijkl->kl', window, subM)
    filtered[wspad:wspad + filtered_data.shape[0], wspad:wspad + filtered_data.shape[1]] = filtered_data

    return filtered

# GRD indices
@timing
def rvi_grd_index(vv, vh):

    """
    RVI - Radar Vegetation Index (Dual Polarization)

    Args:
    VV (array) = Vertical-Vertical polarization
    VH (array) = Vertical-Horizontal polarization
    
    Returns:
        RVI (array) 
    """

    rvi = (4 * vh) / (vv + vh)

    return rvi.astype(np.float32)

@timing
def dpsvi_index(vv, vh):

    """
    DPSVI - Dual Polarization SAR Vegetation Index

    Bibliographic reference here

    Args:
    VV (array) = Vertical-Vertical polarization
    VH (array) = Vertical-Horizontal polarization
    
    Returns:
        DPSVI (array)
    """

    VV_max = np.nanmax(vv)
    
    # np.nanmax(vv) # Maybe use a solver to determine this number

    dpsvi = vh * (VV_max * vh - vv * vh + np.power(vh, 2) + VV_max * vv - np.power(vv, 2) + vh * vv) / (1.4142 * vv)

    return dpsvi.astype(np.float32)

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

# SLC indices    
@timing
def dprvi_index(c11, c12_real, c12_imag, c22, window_size):

    """
    DpRVI - Dual Polarization Radar Vegetation Index

    Args:
    DOP (array) = Degree of polarization
    beta (array) = Dominancy of the scattering mechanism
    
    Returns:
        DpRVI (array) 
    """

    kernel = np.ones((window_size, window_size), np.float32) / (window_size * window_size)

    c11_T1 = c11
    c12_T1 = c12_real + 1j * c12_imag
    c21_T1 = np.conjugate(c12_T1)
    c22_T1 = c22

    c11_T1r = conv2d(np.real(c11_T1), kernel)
    c11_T1i = conv2d(np.imag(c11_T1), kernel)
    c11s = c11_T1r + 1j * c11_T1i

    c12_T1r = conv2d(np.real(c12_T1), kernel)
    c12_T1i = conv2d(np.imag(c12_T1), kernel)
    c12s = c12_T1r + 1j * c12_T1i
    
    c21_T1r = conv2d(np.real(c21_T1), kernel)
    c21_T1i = conv2d(np.imag(c21_T1), kernel)
    c21s = c21_T1r + 1j * c21_T1i

    c22_T1r = conv2d(np.real(c22_T1), kernel)
    c22_T1i = conv2d(np.imag(c22_T1), kernel)
    c22s = c22_T1r + 1j * c22_T1i

    c2_det = (c11s * c22s - c12s * c21s)
    c2_trace = c11s + c22s

    dop = (np.sqrt(1.0 - ((4.0 * c2_det) / np.power(c2_trace, 2))))

    sqdiscr = np.sqrt(np.absolute(np.power(c2_trace, 2) - 4 * c2_det))

    lambda1 = (c2_trace + sqdiscr) * 0.5
    lambda2 = (c2_trace - sqdiscr) * 0.5

    beta = lambda1 / (lambda1 + lambda2)

    dprvi = 1 - (dop * beta)

    return dprvi.astype(np.float32)

@timing
def prvi_index(c11, c12_real, c12_imag, c22, window_size):

    """
    PRVIdp - Polarimetric Radar Vegetation Index (Dual Polarization)

    Args:
    DOP (array) = Degree of polarization
    beta (array) = Dominancy of the scattering mechanism
    
    Returns:
        PRVIdp (array) 
    """

    kernel = np.ones((window_size, window_size), np.float32) / (window_size * window_size)

    c11_T1 = c11
    c12_T1 = c12_real + 1j * c12_imag
    c21_T1 = np.conjugate(c12_T1)
    c22_T1 = c22

    c11_T1r = conv2d(np.real(c11_T1), kernel)
    c11_T1i = conv2d(np.imag(c11_T1), kernel)
    c11s = c11_T1r + 1j * c11_T1i

    c12_T1r = conv2d(np.real(c12_T1), kernel)
    c12_T1i = conv2d(np.imag(c12_T1), kernel)
    c12s = c12_T1r + 1j * c12_T1i
    
    c21_T1r = conv2d(np.real(c21_T1), kernel)
    c21_T1i = conv2d(np.imag(c21_T1), kernel)
    c21s = c21_T1r + 1j * c21_T1i

    c22_T1r = conv2d(np.real(c22_T1), kernel)
    c22_T1i = conv2d(np.imag(c22_T1), kernel)
    c22s = c22_T1r + 1j * c22_T1i
    
    c2_det = (c11s * c22s) - (c12s * c21s)
    c2_trace = c11s + c22s

    dop = (np.sqrt(1.0 - ((4.0 * c2_det) / np.power(c2_trace, 2))))

    prvi = (1 - dop) * c22s

    return prvi.astype(np.float32)

@timing
def _main(settings):

    roi = gpd.read_file(settings['roi_path'])

    geometries = [geom for geom in roi.geometry]

    for i, _ in enumerate(os.listdir(settings['slc_image'])):

        indices_list = []

        slc_image = os.listdir(settings['slc_image'])[i]

        if slc_image.endswith('.tif'):

            slc_file = settings['slc_image'] + '/' + slc_image

            # SAR SLC image
            with rst.open(slc_file) as slc:

                slc_image, slc_transform = mask(slc, geometries, crop=True, nodata=np.nan)

                c11 = slc_image[0]
                c12_real = slc_image[1]
                c12_imag = slc_image[2]
                c22 = slc_image[3]
        
        grd_image = os.listdir(settings['grd_image'])[i]

        if grd_image.endswith('.tif'):

            date = grd_image.split('_')[1]

            grd_file = settings['grd_image'] + '/' + grd_image

            # SAR GRD image
            with rst.open(grd_file) as grd:

                grd_image, grd_transform = mask(grd, geometries, crop=True, nodata=np.nan)

                vh = grd_image[0]
                vv = grd_image[1]
    
        # DpRVI
        dprvi = dprvi_index(c11, c12_real, c12_imag, c22, window_size=1)
        indices_list.append(dprvi)

        # PRVI
        prvi = prvi_index(c11, c12_real, c12_imag, c22, window_size=1)
        indices_list.append(prvi)
            
        # DPSVI
        dpsvi = dpsvi_index(vv, vh)
        indices_list.append(dpsvi)

        # DPSVIm
        dpsvim = dpsvim_index(vv, vh)
        indices_list.append(dpsvim)

        # RVI_GRD
        rvi_grd = rvi_grd_index(vv, vh)
        indices_list.append(rvi_grd)
    
        out_meta = slc.meta

        out_meta.update({
                        "driver": "GTiff",
                        "height": dpsvi.shape[0],
                        "width": dpsvi.shape[1],
                        "transform": slc_transform,
                        "count": len(indices_list)
                        })

        with rst.open(settings['indices_outpath'] + '/' + date + '.tif', "w", **out_meta) as dest:
            for id, indice in enumerate(indices_list, start=1):
                dest.write(indice, id)
        
        print(f'{date} indices processed!')

if __name__ == "__main__":

    import json

    args = _get_args()

    file = open(args.json)

    params = json.load(file)

    _main(params)