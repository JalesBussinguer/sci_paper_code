'''
Sentinel-1 GRD products preprocessing routine

Contents:

- Functions: SNAP operators
- DPSVI preprocessing

Desenvolvido por: Jales de Freitas Bussinguer (UnB)
'''

try:
    from snappy import ProductIO
    from snappy import HashMap
    from snappy import GPF
    from snappy import jpy
except:
    from snappy import ProductIO
    from snappy import HashMap
    from snappy import GPF
    from snappy import jpy

import os
import argparse
import geopandas as gpd
from pathlib import Path
from shapely.geometry import Polygon

import time
from functools import wraps

def timing(func): # Decorator to count the processing time spent on each operator
    @wraps(func)
    def processing_time(*args, **kwargs):
        t1 = time.time()
        result = func(*args, **kwargs)
        t2 = time.time()
        print(f'@timing: {func.__name__} took {t2-t1} seconds')
        return result
    return processing_time
    
def _get_args():

    parser = argparse.ArgumentParser()

    parser.add_argument('-j', '--json',
    help='The input json file cotaining the preprocessing settings',
    type=str)

    args = parser.parse_args()

    return args

def operator_help(operator):

    """
    Operator parameters help - for developers only!

    Shows the parameters of a operator, its default values and a set of other values.

    Args:
    operator (string) = Operator name or alias
    
    Returns:
        Parameter infos of a operator (text)
    """

    op_spi = GPF.getDefaultInstance().getOperatorSpiRegistry().getOperatorSpi(operator)
    print('Operator name: {}'.format(op_spi.getOperatorDescriptor().getName()))
    print('Operator alias: {}\n'.format(op_spi.getOperatorDescriptor().getAlias()))
    print('PARAMETERS:\n')

    param_Desc = op_spi.getOperatorDescriptor().getParameterDescriptors()
        
    for param in param_Desc:
        print('{}: {}\nDefault Value: {}'.format(param.getName(), param.getDescription(), param.getDefaultValue()))
            
        value_set = param.getValueSet()
        print(f'Possible other values: {list(value_set)}\n')

@timing
def ApplyOrbitFile(source):

    """
    Orbit Correction Operator

    The orbit state vectors provided in the metadata of a SAR product are generally not accurate and can be refined with the precise orbit files which are available days-to-weeks after the generation of the product.
    The orbit file provides accurate satellite position and velocity information. Based on this information, the orbit state vectors in the abstract metadata of the product are updated.

    Args:
    source (product) = Sentinel-1 product object
    
    Returns:
        Orbit rectified product (product)
    """

    parameters = HashMap()

    parameters.put('orbitType', 'Sentinel Precise (Auto Download)') # Orbit type
    parameters.put('polyDegree', '3') # Polynomial Degree
    parameters.put('continueOnFail', 'true') # Stop the code if the orbit metadata can't be found

    return GPF.createProduct('Apply-Orbit-File', parameters, source)

@timing
def ThermalNoiseReduction(source):
    
    """
    Thermal Noise Reduction Operator

    Thermal noise correction can be applied to Sentinel-1 Level-1 SLC products as well as Level-1 GRD products which have not already been corrected. 
    The operator can also remove this correction based on the product annotations (i.e. to re-introduce the noise signal that was removed). 
    Product annotations will be updated accordingly to allow for re-application of the correction.

    Args:
    source (prodcut) = Sentinel-1 product object
    
    Returns:
        Thermal Noise corrected product (product)
    """

    parameters = HashMap()
    
    parameters.put('selectedPolarisations', 'VH,VV')
    parameters.put('removeThermalNoise', True)

    return GPF.createProduct('Thermal-Noise-Reduction', parameters, source)

@timing
def Calibration(source):

    """
    Radiometric Calibration Operator

    The objective of SAR calibration is to provide imagery in which the pixel values can be directly related to the radar backscatter of the scene. 
    Though uncalibrated SAR imagery is sufficient for qualitative use, calibrated SAR images are essential to quantitative use of SAR data.

    This Operator performs different calibrations for Sentinel-1 products deriving the sigma nought images. 
    Optionally gamma nought and beta nought images can also be created.

    Args:
    source (product) = Sentinel-1 product object
    
    Returns:
        Calibrated image (product)
    """   

    parameters = HashMap()

    parameters.put('outputSigmaBand', True)
    parameters.put('sourceBands', 'Amplitude_VH,Amplitude_VV')
    parameters.put('selectedPolarisations', 'VH,VV')
    parameters.put('outputImageScaleInDb', False)

    return GPF.createProduct('Calibration', parameters, source)

@timing
def SpeckleFilter(source, filter, size_x=3, size_y=3):

    """
    Speckle Filter Operator

    SAR images have inherent salt and pepper like texturing called speckles which degrade the quality of the image and make interpretation of features more difficult. 
    Speckles are caused by random constructive and destructive interference of the de-phased but coherent return waves scattered by the elementary scatters within each resolution cell. 
    Speckle noise reduction can be applied either by spatial filtering or multilook processing.

    Filters supported: 'Boxcar', 'Median', 'Frost', 'Gamma Map', 'Lee', 'Refined Lee', 'Lee Sigma', 'IDAN'

    Args:
    source (array) = Sentinel-1 product
    filter (string) = selected filter
    size_x = size of the moving window in x. Default = 3
    seize_y = size of the the moving window in y. Default = 3
    
    Returns:
        Calibrated image (array)
    """ 

    parameters = HashMap()

    parameters.put('sourceBands', 'Sigma0_VH,Sigma0_VV')
    parameters.put('filter', filter)
    parameters.put('filterSizeX', size_x)
    parameters.put('filterSizeY', size_y)

    return GPF.createProduct('Speckle-Filter', parameters, source)

@timing
def TerrainCorrection(source):

    """
    Range Doppler Terrain Correction Operator

    Due to topographical variations of a scene and the tilt of the satellite sensor, distances can be distorted in the SAR images. 
    Image data not directly at the sensor's Nadir location will have some distortion. 
    Terrain corrections are intended to compensate for these distortions so that the geometric representation of the image will be as close as possible to the real world.

    Args:
    source (array) = Sentinel-1 product
    
    Returns:
        Terrain corrected image (array)
    """ 

    parameters = HashMap()

    parameters.put('demName', 'SRTM 3Sec')
    parameters.put('demResamplingMethod', 'BILINEAR_INTERPOLATION')
    parameters.put('imgResamplingMethod', 'BILINEAR_INTERPOLATION')
    parameters.put('mapProjection', 'EPSG:32723')
    parameters.put('pixelSpacingInMeter', 10.0)
    parameters.put('sourceBands', 'Sigma0_VH,Sigma0_VV')

    return GPF.createProduct('Terrain-Correction', parameters, source)

@timing
def Subset(source, wkt):

    """
    Subset Operator

    This operator is used to create either spatial and/or spectral subsets of a data product. 
    Spatial subset may be given by pixel positions or a geographical polygon.

    Args:
    source (array) = Sentinel-1 product
    wkt (string) = The subset region in geographical coordinates using WKT-format.
    
    Returns:
        A scene subset image (array)
    """ 

    parameters = HashMap()

    parameters.put('geoRegion', wkt)

    return GPF.createProduct('Subset', parameters, source)

@timing
def _get_georegion_wkt(roi_path):

    """
    Gets the wkt of the region of interest. This wkt is used to subset the imagery.

    The roi file must be a GeoJSON file with a geographic coodinate system (ex. EPSG 4326)

    Args:
    roi_path (string) = path to the roi GeoJSON file
    
    Returns:
        roi wkt (string)
    """ 

    gdf = gpd.read_file(roi_path, dtype=object)

    geom = gdf.geometry.buffer(0.002).unary_union
    bounds = geom.bounds
    bbox = Polygon.from_bounds(*bounds)
    wkt = bbox.wkt

    return wkt

def _dpsvi_preprocessing(product, roi_wkt, outpath, date):

    S1_Orb = ApplyOrbitFile(product)

    S1_Orb_Cal = Calibration(S1_Orb)

    S1_Orb_Cal_Spk = SpeckleFilter(S1_Orb_Cal, 'Refined Lee')

    S1_Orb_Cal_Spk_TC = TerrainCorrection(S1_Orb_Cal_Spk)

    S1_Orb_Cal_Spk_Sub = Subset(S1_Orb_Cal_Spk_TC, wkt=roi_wkt)

    ProductIO.writeProduct(S1_Orb_Cal_Spk_Sub, outpath + '/' + 'S0'+'_'+date+'_32723', 'GeoTIFF')

    return print('GRD product preprocessing for DPSVI: Done')

@timing
def _main(settings):

    # GPF Initialization
    GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()

    # Getting the roi wkt for subset
    roi_wkt = _get_georegion_wkt(settings['roi_path'])

    if not os.path.exists(settings['outpath']):
        os.makedirs(settings['outpath'])
    
    func_dict = {
        'dpsvi': _dpsvi_preprocessing
    }
    
    preprocessing_method = settings['preprocessing_method']

    System = jpy.get_type('java.lang.System')

    for item in os.listdir(settings['path']):

        if item.endswith('.zip'):

            date = item.split('_')[4]

            product = ProductIO.readProduct(settings['path'] + '/' + item)

            selected_func = func_dict[preprocessing_method] if preprocessing_method in func_dict else None

            assert selected_func is not None, f'Unknown processing method! {preprocessing_method}'

            selected_func(product, roi_wkt, settings['outpath'], date)

            product.dispose()
            System.gc()

if __name__ == "__main__":

    import json

    args = _get_args()

    file = open(args.json)

    params = json.load(file)

    _main(params)

    cache_path = params['cache_path']

    for p in Path(cache_path).glob("*.tmp"):
        os.remove(p)