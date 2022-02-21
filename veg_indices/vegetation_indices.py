import argparse
import numpy as np
import rasterio as rst
from rasterio.mask import mask

import geopandas as gpd

import time
from functools import wraps

def _get_args():

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

# Optical indices
@timing
def ndvi_index(nir, red):

    """
    NDVI - Normalized Difference Vegetation Index

    Args:
        nir (array): near infrared band (S2-B8)
        red (array): red band (S2-B4)

    Returns:
        NDVI (array)
    """

    ndvi = (nir - red) / (nir + red)
    
    return ndvi.astype(np.float32)

@timing
def ndwi_index(nir, swir1):

    """
    NDWI - Normalized Difference Water Index

    Args:
        nir (array): near infrared band (S2-B8)
        swir1 (array) = short wave infrared band (S2-B11)

    Returns:
        NDWI (array)
    """

    ndwi = (nir - swir1) / (nir + swir1)
    
    return ndwi.astype(np.float32)

@timing
def psri_index(red, blue, redge2):

    """
    PSRI - Plant Senescence Reflectance Index

    Args:
    red (array) = red band (S2-B4)
    blue (array) = blue band (S2-B2)
    redge2 (array) = red edge 2 band (S2-B6)

    Returns:
        PSRI (array)
    """

    psri = (red - blue) / redge2
    
    return psri.astype(np.float32)

@timing
def evi_index(nir, red, blue):

    '''
    EVI - Enhanced Vegetation Index

    Args:
    nir (array) = near infrared band (S2-B8)
    red (array) = red band (S2-B4)
    blue (array) = blue band (S2-B2)
    
    Returns:
        EVI (array) 
    '''

    evi = 2.5 * ((nir - red) / (nir + (6 * red) - (7.5 * blue) + 1))

    return evi.astype(np.float32)

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

    rvi = (4 * vv) / (vv + vh)

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

    VV_max = 0.25
    
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

    return dpsvim.astype(np.float32) * 10

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

    beta = np.abs(lambda1 / (lambda1 + lambda2))

    dprvi = np.abs(1 - (dop * beta))

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

    prvi = np.abs((1 - dop) * c22s)

    return prvi.astype(np.float32) * 10

# @timing
# def rvi_slc_index(c11, c22, window_size):

#     kernel = np.ones((window_size, window_size), np.float32) / (window_size * window_size)

#     c11_T1 = c11
#     c22_T1 = c22

#     c11_T1r = conv2d(np.real(c11_T1), kernel)
#     c11_T1i = conv2d(np.imag(c11_T1), kernel)
#     c11s = c11_T1r + 1j * c11_T1i

#     c22_T1r = conv2d(np.real(c22_T1), kernel)
#     c22_T1i = conv2d(np.imag(c22_T1), kernel)
#     c22s = c22_T1r + 1j * c22_T1i
    
#     c2_trace = c11s + c22s

#     rvi = (4 * c22s) / c2_trace

#     return rvi.astype(np.float32)

@timing
def _main(settings):

    roi = gpd.read_file(settings['roi_path'])

    geometries = [geom for geom in roi.geometry]

    # Optical image
    with rst.open(settings['optical_image']) as opt:
        
        opt_image, opt_transform = mask(opt, geometries, crop=True, nodata=np.nan)
        
        swir = opt_image[0]
        nir = opt_image[1]
        redge = opt_image[2]
        red = opt_image[3]
        green = opt_image[4]
        blue = opt_image[5]

    # SAR GRD image
    with rst.open(settings['grd_image']) as grd:

        grd_image, grd_transform = mask(grd, geometries, crop=True, nodata=np.nan)

        vh = grd_image[0]
        vv = grd_image[1]
    
    # SAR SLC image
    with rst.open(settings['slc_image']) as slc:

        slc_image, slc_transform = mask(slc, geometries, crop=True, nodata=np.nan)

        c11 = slc_image[0]
        c12_real = slc_image[1]
        c12_imag = slc_image[2]
        c22 = slc_image[3]
    
    indices_list = []
    
    # Multispectral vegetation indices

    # NDVI
    ndvi = ndvi_index(nir, red)
    indices_list.append(ndvi)
    # NDWI
    ndwi = ndwi_index(nir, swir)
    indices_list.append(ndwi)
    # PSRI
    psri = psri_index(red, blue, redge)
    indices_list.append(psri)
    # EVI
    evi = evi_index(nir, red, blue)
    indices_list.append(evi)
    
    # SAR vegetation indices

    # DpRVI
    dprvi = dprvi_index(c11, c12_real, c12_imag, c22, window_size=3)
    indices_list.append(dprvi)
    # PRVI
    prvi = prvi_index(c11, c12_real, c12_imag, c22, window_size=3)
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

    out_meta = opt.meta

    out_meta.update({
                    "driver": "GTiff",
                    "height": ndvi.shape[0],
                    "width": ndvi.shape[1],
                    "transform": opt_transform,
                    "count": len(indices_list)
                    })

    with rst.open(settings['indices_outpath'], "w", **out_meta) as dest:
        for id, indice in enumerate(indices_list):
            dest.write_band(indice, id)

if __name__ == "__main__":

    import json

    args = _get_args()

    file = open(args.json)

    params = json.load(file)

    _main(params)