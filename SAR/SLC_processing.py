'''
Sentinel-1 SLC products preprocessing routine

Contents:

- Functions: SNAP operators
- PRVI preproccessing
- DpRVI preprocessing
- Polarimetric Decomposition processing
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

import stsa
import numpy as np
import geopandas as gpd
from shapely.geometry import Polygon

import os
from pathlib import Path
import argparse

import time
from functools import wraps

def timing(func): # Processing time decorator
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
def swath_detection(file, roi_path):

    roi = gpd.read_file(roi_path)

    s1 = stsa.TopsSplitAnalyzer(target_subswaths=['iw1', 'iw2', 'iw3'], polarization='vh')
    s1.load_zip(file)

    s1.get_subswath_geometries()

    gdf = s1.df
    spatial_join = gpd.sjoin(gdf, roi, how='inner', op='intersects')

    swaths = spatial_join['subswath'].unique()
    
    iw_dict = {}

    for sw in swaths:
        burst_values = spatial_join[spatial_join.subswath == sw]['burst'].values
        iw_dict[sw] = (np.min(burst_values), np.max(burst_values))

    return iw_dict

@timing
def TopsarSplit(source, subswath, bursts):

    """
    TOPSAR Split Operator

    The TOPSAR Split operator provides a convenient way to split each subswath with selected bursts into a separate product. \n
    This operator detects of the swaths and its bursts of the scene in a automated way.

    Args:
        source (product) = Sentinel-1 multi-swath SLC product (e.g. IW product with VH and VV polarisations) \n
        file (string) = filename of the SAR product \n
        roi_path (string) = path to the roi file
    
    Returns:
        Split Sentinel-1 product with the selected subswath, bursts and polarisations (product).
    """
    parameters = HashMap()

    parameters.put('subswath', subswath)
    parameters.put('selectedPolarisations', 'VH,VV')
    parameters.put('firstBurstIndex', bursts[0])
    parameters.put('lastBurstIndex', bursts[-1])
    
    return GPF.createProduct('TOPSAR-Split', parameters, source)

@timing
def ApplyOrbitFile(source):

    """
    Orbit Correction Operator

    The orbit state vectors provided in the metadata of a SAR product are generally not accurate and can be refined with the precise orbit files which are available days-to-weeks after the generation of the product.
    The orbit file provides accurate satellite position and velocity information. Based on this information, the orbit state vectors in the abstract metadata of the product are updated.

    Args:
    source (product) = Sentinel-1 product object
    
    Returns:
        Orbit corrected image (product)
    """

    # The parameters are static for all preprocessing routines

    parameters = HashMap()

    parameters.put('orbitType', 'Sentinel Precise (Auto Download)') # Orbit type
    parameters.put('polyDegree', '3') # Polynomial Degree
    parameters.put('continueOnFail', 'false') # Stop the code if the orbit metadata can't be found

    return GPF.createProduct('Apply-Orbit-File', parameters, source)

@timing
def ThermalNoiseRemoval(source):

    parameters = HashMap()

    parameters.put('selectedPolarisations', 'VH,VV') # Polarisations
    parameters.put('removeThermalNoise', 'true') # Remove Thermal Noise

    return GPF.createProduct('ThermalNoiseRemoval', parameters, source)

@timing
def Calibration(source):

    """
    Radiometric Calibration Operator

    The objective of SAR calibration is to provide imagery in which the pixel values can be directly related to the radar backscatter of the scene. 
    Though uncalibrated SAR imagery is sufficient for qualitative use, calibrated SAR images are essential to quantitative use of SAR data.

    This Operator performs different calibrations for Sentinel-1 products deriving the sigma nought images. 
    Optionally gamma nought and beta nought images can also be created.

    Args:
    source (product) = Sentinel-1 product
    complex (bool) = Calibration output in complex. Default = False
    
    Returns:
        Calibrated image (product)
    """   

    parameters = HashMap()

    parameters.put('selectedPolarisations', 'VH,VV')
    parameters.put('outputSigmaBand', 'true')
    parameters.put('outputImageScaleInDb', 'false')

    return GPF.createProduct('Calibration', parameters, source)

@timing
def TopsarDeburst(source):

    """
    TOPSAR Deburst Operator

    For the TOPSAR IW and EW SLC products, each product consists of one image per swath per polarization. 
    IW products have 3 swaths and EW have 5 swaths. 
    Each sub-swath image consists of a series of bursts, where each burst was processed as a separate SLC image. 
    The individually focused complex burst images are included, in azimuth-time order, into a single subswath image, with black-fill demarcation in between, similar to the ENVISAT ASAR Wide ScanSAR SLC products.

    Args:
    source (product) = Sentinel-1 product
    
    Returns:
        Debursted product (product)
    """  

    parameters  = HashMap()

    parameters.put('selectedPolarisations', 'VH,VV')

    return GPF.createProduct('TOPSAR-Deburst', parameters, source)

@timing
def TopsarMerge(source):

    """
    TOPSAR Merge Operator

    The TOPSAR Merge operator merges the debursted split product of different sub-swaths into on complete product. 
    The merge happens only in range in the same fashion as in TOPSAR Deburst operator.

    Args:
    source (product) = Sentinel-1 product
    
    Returns:
        Merged product (product)
    """ 

    parameters = HashMap()

    parameters.put('selectedPolarisations', 'VH,VV')

    return GPF.createProduct('TOPSAR-Merge', parameters, source)

@timing
def Multilooking(source):

    """
    Multilooking Operator

    Generally, a SAR original image appears speckled with inherent speckle noise. 
    To reduce this inherent speckled appearance, several images are incoherently combined as if they corresponded to different looks of the same scene. 
    This processing is generally known as multilook processing. 
    As a result the multilooked image improves the image interpretability. 
    Additionally, multilook processing can be used to produce an application product with nominal image pixel size.

    This operator implements the space-domain multilook method by averaging a single look image with a small sliding window.

    Args:
    source (product) = Sentinel-1 product
    
    Returns:
        Multilooked product (product)
    """

    parameters = HashMap()

    parameters.put('nRgLooks', 4)
    parameters.put('nAzLooks', 1)
    parameters.put('outputIntensity', 'true')
    parameters.put('grSquarePixel', 'true')

    return GPF.createProduct('Multilook', parameters, source)

@timing
def SR2GR(source):

    parameters = HashMap()

    parameters.put('warpPolynomialOrder', 4)
    parameters.put('interpolationMethod', 'Nearest-neighbor interpolation')

    return GPF.createProduct('SRGR', parameters, source)

@timing
def C2_Matrix(source):

    """
    Polarimetric Matrices Operator

    This operator creates polarimetric 2 x 2 covariance matrix (C2).

    Args:
    source (product) = Sentinel-1 product
    
    Returns:
        C2 matrix product (product)
    """

    parameters = HashMap()

    parameters.put('matrix', 'C2')

    return GPF.createProduct('Polarimetric-Matrices', parameters, source)

@timing
def PolarimetricSpeckleFilter(source, filter, window_size='5x5'):

    """
    Polarimetric Speckle Filter Operator

    SAR images have inherent salt and pepper like texturing called speckles which degrade the quality of the image and make interpretation of features more difficult. 
    Speckles are caused by random constructive and destructive interference of the de-phased but coherent return waves scattered by the elementary scatters within each resolution cell. 
    Speckle noise reduction can be applied either by spatial filtering or multilook processing.

    Filters supported: 'Box Car Filter', 'IDAN FIlter', 'Refined Lee Filter', 'Improved Lee Sigma Filter'

    Number of Looks supported: '1', '2', '3', '4'

    Window sizes supported: '5x5', '7x7', '9x9', '11x11', '13x13', '15x15', '17x17'

    Args:
    source (product) = Sentinel-1 product object
    filter (string) = Polarimetric filter (see filters supported)
    window_size (string) = Sliding window size. Default: '5x5'
    
    Returns:
        Calibrated image (product)
    """ 

    parameters = HashMap()

    parameters.put('filter', filter)
    parameters.put('numLooksStr', '1')
    parameters.put('windowSize', window_size)
    
    return GPF.createProduct('Polarimetric-Speckle-Filter', parameters, source)

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

    parameters.put('filter', filter)
    parameters.put('filterSizeX', size_x)
    parameters.put('filterSizeY', size_y)
    parameters.put('estimateENL', 'true')

    return GPF.createProduct('Speckle-Filter', parameters, source)

@timing
def PolarimetricDecomposition(source, window_size='3'):

    """
    Polarimetric Decomposition Operator

    This operator performs the polarimetric decomposition for SAR SLC products.

    Args:
    source (product) = Sentinel-1 product object
    window_size (int) = Sliding window size. Default: 3
    
    Returns:
        Calibrated image (product)
    """ 

    parameters = HashMap()

    parameters.put('decomposition', 'H-Alpha Dual Pol Decomposition')
    parameters.put('windowSize', window_size)

    return GPF.createProduct('Polarimetric-Decomposition', parameters, source)

@timing
def TerrainCorrection(source):

    """
    Range Doppler Terrain Correction Operator

    Due to topographical variations of a scene and the tilt of the satellite sensor, distances can be distorted in the SAR images. 
    Image data not directly at the sensor's Nadir location will have some distortion. 
    Terrain corrections are intended to compensate for these distortions so that the geometric representation of the image will be as close as possible to the real world.

    Args:
    source (product) = Sentinel-1 product
    
    Returns:
        Terrain corrected image (product)
    """ 

    parameters = HashMap()

    parameters.put('demName', 'SRTM 3Sec')
    parameters.put('demResamplingMethod', 'BILINEAR_INTERPOLATION')
    parameters.put('imgResamplingMethod', 'BILINEAR_INTERPOLATION')
    parameters.put('mapProjection', 'EPSG:32723')
    parameters.put('pixelSpacingInMeter', 10.0)

    return GPF.createProduct('Terrain-Correction', parameters, source)

@timing
def Subset(source, wkt):

    """
    Subset Operator

    This operator is used to create either spatial and/or spectral subsets of a data product. 
    Spatial subset may be given by pixel positions or a geographical polygon.

    Args:
    source (product) = Sentinel-1 product
    wkt (string) = The subset region in geographical coordinates using WKT-format.
    
    Returns:
        A scene subset image (product)
    """ 

    parameters = HashMap()

    parameters.put('geoRegion', wkt)
    parameters.put('copyMetadata', 'true')

    return GPF.createProduct('Subset', parameters, source)

@timing
def get_georegion_wkt(roi_path):

    """
    Gets the wkt of the region of interest. This wkt is used to subset the imagery.

    The roi file must be a GeoJSON file with a geographic coodinate system (ex. EPSG 4326)

    Args:
    roi_path (string) = path to the roi GeoJSON file
    
    Returns:
        roi wkt (string)
    """ 

    gdf = gpd.read_file(roi_path, dtype=object)

    geom = gdf.geometry.buffer(0.02).unary_union
    bounds = geom.bounds
    bbox = Polygon.from_bounds(*bounds)
    wkt = bbox.wkt

    return wkt

@timing
def slc2grd(product, roi_wkt, outpath, file, date, roi_path):

    iw_dict = swath_detection(file, roi_path)

    product_dict = {}

    for swath, bursts in iw_dict.items():

        S1_split = TopsarSplit(product, swath, bursts)

        S1_split_Orb = ApplyOrbitFile(S1_split)

        #S1_split_Orb_TNR = ThermalNoiseRemoval(S1_split_Orb)

        S1_split_Orb_TNR_Cal = Calibration(S1_split_Orb)

        S1_split_Orb_TNR_Cal_Deb = TopsarDeburst(S1_split_Orb_TNR_Cal)

        product_dict[swath] = S1_split_Orb_TNR_Cal_Deb

    products = list(product_dict.values())

    S1_split_Orb_TNR_Cal_Deb_Merge = TopsarMerge(products) if len(products) > 1 else products[0]

    S1_split_Orb_TNR_Cal_Deb_Merge_Mul = Multilooking(S1_split_Orb_TNR_Cal_Deb_Merge)

    S1_split_Orb_TNR_Cal_Deb_Merge_Mul_Spk = SpeckleFilter(S1_split_Orb_TNR_Cal_Deb_Merge_Mul, 'Refined Lee') #5x5

    S1_split_Orb_TNR_Cal_Deb_Merge_Mul_Spk_SRGR = SR2GR(S1_split_Orb_TNR_Cal_Deb_Merge_Mul_Spk)

    S1_split_Orb_TNR_Cal_Deb_Merge_Mul_Spk_SRGR_Ter = TerrainCorrection(S1_split_Orb_TNR_Cal_Deb_Merge_Mul_Spk_SRGR)

    S1_split_Orb_TNR_Cal_Deb_Merge_Mul_Spk_SRGR_Ter_Sub = Subset(S1_split_Orb_TNR_Cal_Deb_Merge_Mul_Spk_SRGR_Ter, wkt=roi_wkt)

    ProductIO.writeProduct(S1_split_Orb_TNR_Cal_Deb_Merge_Mul_Spk_SRGR_Ter_Sub, outpath + '/' + 'GRD' + '_' + date + '_' + '32723', 'GeoTIFF')

    return print('SLC TO GRD: Done')

@timing
def pol_decomposition(product, roi_wkt, outpath, file, date, roi_path):

    iw_dict = swath_detection(file, roi_path)

    product_dict = {}

    for swath, bursts in iw_dict.items():

        S1_split = TopsarSplit(product, swath, bursts)

        S1_split_Orb = ApplyOrbitFile(S1_split)

        S1_split_Orb_Deb = TopsarDeburst(S1_split_Orb)

        product_dict[swath] = S1_split_Orb_Deb

    products = list(product_dict.values())

    S1_split_Orb_Deb_Merge = TopsarMerge(products) if len(products) > 1 else products[0]

    S1_split_Orb_Deb_Sub = Subset(S1_split_Orb_Deb_Merge, wkt=roi_wkt)

    S1_split_Orb_Deb_Sub_Mul = Multilooking(S1_split_Orb_Deb_Sub)

    S1_split_Orb_Deb_Sub_Mul_Spk = PolarimetricSpeckleFilter(S1_split_Orb_Deb_Sub_Mul, 'Refined Lee Filter')

    S1_split_Orb_Deb_Sub_Mul_Spk_Decomp = PolarimetricDecomposition(S1_split_Orb_Deb_Sub_Mul_Spk)

    S1_split_Orb_Deb_Sub_Mul_Spk_Decomp_Ter = TerrainCorrection(S1_split_Orb_Deb_Sub_Mul_Spk_Decomp)

    ProductIO.writeProduct(S1_split_Orb_Deb_Sub_Mul_Spk_Decomp_Ter, outpath + '/' + 'S1_split_Orb_Cal_Deb_Sub_Mul_C2_Spk_Decomp_TC' + '_' + date + '_' + '32723', 'GeoTIFF')

    return print('Polarimetric Decomposition: Done')

@timing
def prvi_preprocessing(product, roi_wkt, outpath, file, date, roi_path):

    iw_dict = swath_detection(file, roi_path)

    product_dict = {}

    for swath, bursts in iw_dict.items():

        S1_split = TopsarSplit(product, swath, bursts)

        S1_split_Orb = ApplyOrbitFile(S1_split)

        S1_split_Orb_Cal = Calibration(S1_split_Orb)

        S1_split_Orb_Cal_Deb = TopsarDeburst(S1_split_Orb_Cal)

        product_dict[swath] = S1_split_Orb_Cal_Deb

    products = list(product_dict.values())

    S1_split_Orb_Deb_Merge = TopsarMerge(products) if len(products) > 1 else products[0]

    S1_split_Orb_Cal_Deb_Mul = Multilooking(S1_split_Orb_Deb_Merge)

    S1_split_Orb_Cal_Deb_Mul_C2 = C2_Matrix(S1_split_Orb_Cal_Deb_Mul)

    S1_split_Orb_Cal_Deb_Mul_C2_Spk = PolarimetricSpeckleFilter(S1_split_Orb_Cal_Deb_Mul_C2, 'Refined Lee Filter')

    S1_split_Orb_Cal_Deb_Mul_C2_Spk_TC = TerrainCorrection(S1_split_Orb_Cal_Deb_Mul_C2_Spk)

    S1_split_Orb_Cal_Deb_Mul_C2_Spk_TC_Sub = Subset(S1_split_Orb_Cal_Deb_Mul_C2_Spk_TC, wkt=roi_wkt)

    ProductIO.writeProduct(S1_split_Orb_Cal_Deb_Mul_C2_Spk_TC_Sub, outpath + '/' + 'GRD'+'_'+date+'_'+'32723', 'GeoTIFF')

    return print('SLC preprocessing for PRVI: Done')

@timing
def _main(settings):

    # GPF Initialization
    GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()

    # Getting the roi wkt for subset
    roi_wkt = get_georegion_wkt(settings['roi_path'])

    if not os.path.exists(settings['outpath']):
        os.makedirs(settings['outpath'])
    
    func_dict = {
        'prvi': prvi_preprocessing,
        'pol_decomposition': pol_decomposition,
        'slc2grd': slc2grd
    }
    
    preprocessing_method = settings['preprocessing_method']

    System = jpy.get_type('java.lang.System')
    
    for item in os.listdir(settings['path']):

        if item.endswith('.zip'):

            date = item.split('_')[5]

            file = settings['path'] + '/' + item

            product = ProductIO.readProduct(file)

            selected_func = func_dict[preprocessing_method] if preprocessing_method in func_dict else None

            assert selected_func is not None, f'Unknown processing method! {preprocessing_method}'

            selected_func(product, roi_wkt, settings['outpath'], file, date, settings['roi_path'])

            product.dispose()
            System.gc()

if __name__== "__main__":

    import json

    args = _get_args()

    file = open(args.json)

    params = json.load(file)

    _main(params)

    cache_path = params['cache_path']

    for p in Path(cache_path).glob("*.tmp"):
        os.remove(p)