"""
S1-GRD preprocessing routine

Author: Jales Bussinguer
"""

# Imports
# Basic Libraryimport numpy as np

# Snappy modules
from snappy import ProductIO
from snappy import HashMap
from snappy import GPF
from snappy import jpy
from snappy import WKTReader

# def subset_by_shape(data, shape):
    
#     g = []

#     wkt = str(m.wkt).replace('MULTIPOINT', 'POLYGON(') +')'

#     SubsetOp = jpy.get_type('org.esa.snap.core.gpf.common.SubsetOp')

#     limites = wkt

#     geometria = WKTReader().read(limites)

#     HashMap = jpy.get_type('java.util.HashMap')
#     GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()

#     parameters = HashMap()
#     parameters.put('copyMetadata', True)
#     parameters.put('geoRegion', geometria)

#     subset = GPF.createProduct('Subset', parameters, data)
    
#     return subset

# Ortorretificação (Orthorectification) - Apply Orbit File

def apply_orbit_file(data):

    """
    Apply Orbit File

    Args:
        data ([type]): [description]

    Returns:
        [type]: [description]
    """

    print('Aplying Orbit File...')

    parameters = HashMap()

    parameters.put('orbitType', 'Sentinel Precise (Auto Download)')
    parameters.put('polyDegree', '3')
    parameters.put('continueOnFail', 'false')

    return GPF.createProduct('Apply-Orbit-File', parameters, data)

# Informações - Information

def ProductInformation(data):

    """
    Gets the product basic informations

    Args:
        data

    Returns:
        [type]: [description]
    """

    print('Getting product informations...')

    # Getting the width of the scene
    width = data.getSceneRasterWidth()
    print('Width: {} px'.format(width))

    # Getting the height of the scene
    height = data.getSceneRasterHeight()
    print('Height: {} px'.format(height))

    # Getting the dataset name
    name = data.getName()
    print('Name: {}'.format(name))

    # Getting the band names in the imagery
    band_names = data.getBandNames()
    print('Band names: {}'.format(', '.join(band_names)))

    return width, height, name, band_names

def Calibration(data, band, pol):

    """
    Radiometric Calibration

    Args:
        data ([type]): [description]
        band ([type]): [description]
        polarization (string): 'VV' or 'VH'

    Returns:
        [type]: [description]
    """

    print('Calibrating...')
    
    parameters = HashMap()

    parameters.put('outputSigmaBand', True) 
    parameters.put('sourceBands', band)
    parameters.put('selectedPolarisations', pol)
    parameters.put('outputImageScaleInDb', False)

    return GPF.createProduct('Calibration', parameters, data)

# Filtragem Speckle - Speckle Filtering

def SpeckleFilter(data, source_band, filter, filterSizeX, filterSizeY):

    """
    Speckle Filtering

    Args:
        data ([type]): [description]
        source_band ([type]): [description]
        filter (string): 'VV' or 'VH'
        filterSizeX (int):
        filterSizeY (int):

    Returns:
        [type]: [description]
    """

    print('Aplying the Speckle Filter...')

    parameters = HashMap()

    parameters.put('sourceBands', source_band)
    parameters.put('filter', filter)
    parameters.put('filterSizeX', '%s' % (filterSizeX))
    parameters.put('filterSizeY', '%s' % (filterSizeY))
    parameters.put('dampingFactor', '2')
    parameters.put('estimateENL', 'true')
    parameters.put('enl', '1.0')
    parameters.put('numLooksStr', '1')
    parameters.put('targetWindowSizeStr', '3x3')
    parameters.put('sigmaStr', '0.9')
    parameters.put('anSize', '50')

    return GPF.createProduct('Speckle-Filter', parameters, data)

def Terrain_Correction(data, source_band):

    """
    Range Doppler Terrain Correction

    Args:
        data ([type]): [description]
        source_band (string): [description]

    Returns:
        [type]: [description]
    """

    print('Aplying the Range Doppler Terrain Correction...')

    parameters = HashMap()

    parameters.put('demName', 'SRTM 3Sec')
    parameters.put('demResamplingMethod', 'BILINEAR_INTERPOLATION')
    parameters.put('imgResamplingMethod', 'BILINEAR_INTERPOLATION')
    parameters.put('pixelSpacingInMeter', 10.0)
    parameters.put('sourceBands', source_band)

    return GPF.createProduct('Terrain-Correction', parameters, data)

def listParams(operator_name):

    """
    list the parameters of a SNAP operator

    Args:
        operator_name (string): [description]

    Returns:
        [type]: [description]
    """

    GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()
    
    op_spi = GPF.getDefaultInstance().getOperatorSpiRegistry().getOperatorSpi(operator_name)

    print('Operator name:', op_spi.getOperatorDescriptor().getName())
    print('Operator alias:', op_spi.getOperatorDescriptor().getAlias())

    param_desc = op_spi.getOperatorDescriptor().getParameterDescriptors()

    for param in param_desc:
        print(param.getName(), 'or', param.getAlias())

if __name__ == '__main__':

    # GPF Initialization
    GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()

    # Product initialization
    s1_path = 'C:/Users/jales/Desktop/S1A.zip'

    # Reading the data
    product = ProductIO.readProduct(s1_path)
