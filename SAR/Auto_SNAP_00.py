"""
S1-GRD preprocessing routine

Author: Jales Bussinguer

"""

# Imports
# Basic Library
import numpy as np

# Snappy modules
from snappy import ProductIO
from snappy import HashMap
from snappy import GPF
from snappy import jpy
from snappy import WKTReader

def subset_by_shape(data, shape):
    
    g = []

    wkt = str(m.wkt).replace('MULTIPOINT', 'POLYGON(') +')'

    SubsetOp = jpy.get_type('org.esa.snap.core.gpf.common.SubsetOp')

    limites = wkt

    geometria = WKTReader().read(limites)

    HashMap = jpy.get_type('java.util.HashMap')
    GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()

    parameters = HashMap()
    parameters.put('copyMetadata', True)
    parameters.put('geoRegion', geometria)

    subset = GPF.createProduct('Subset', parameters, data)
    
    return subset

# Ortorretificação (Orthorectification) - Apply Orbit File

def ApplyOrbitFile(data):
    """[summary]

    Args:
        data ([type]): [description]

    Returns:
        [type]: [description]
    """
    print('Aplying Orbit File...')

    parameters = HashMap()

    GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()

    parameters.put('orbitType', 'Sentinel Precise (Auto Download)')
    parameters.put('polyDegree', '3')
    parameters.put('continueOnFail', 'false')

    return GPF.createProduct('Apply-Orbit-File', parameters, data)

# Informações - Information

def ProductInformation(data):

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

# Calibração Radiométrica - Radiometric Calibration

def Calibration(data, band, pol):

    print('Calibrating...')
    
    parameters = HashMap()

    parameters.put('outputSigmaBand', True) 
    parameters.put('sourceBands', band)
    parameters.put('selectedPolarisations', pol)
    parameters.put('outputImageScaleInDb', False)

    return GPF.createProduct('Calibration', parameters, data)

# Filtragem Speckle - Speckle Filtering

def SpeckleFilter(data, source_band, filter, filterSizeX, filterSizeY):

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

# Correção Geométrica (Range Doppler Terrain Correction)

def Terrain_Correction(data, source_band):

    print('Aplying the Range Doppler Terrain Correction...')

    parameters = HashMap()

    parameters.put('demName', 'SRTM 3Sec')
    parameters.put('demResamplingMethod', 'BILINEAR_INTERPOLATION')
    parameters.put('imgResamplingMethod', 'BILINEAR_INTERPOLATION')
    parameters.put('pixelSpacingInMeter', 10.0)
    parameters.put('sourceBands', source_band)

    return GPF.createProduct('Terrain-Correction', parameters, data)

# Conversão para decibel (LinearToFromdB)

def Convert_to_dB(data, source_band):
    
    print('Converting to dB...')

    parameters = HashMap()

    parameters.put('sourceBands', source_band)

    return GPF.createProduct('LinearToFromdB', parameters, data)

# Função que lista os parâmetros de cada operador do SNAP

def listParams(operator_name):

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

    # ------------------------------------------------------------------------------------------------------

    ProductInformation(product)

    S1_Sub = Subset(product, 0, 9928, 25580, 16846)

    print('Imagem recortada: 100%')

    S1_Sub_Orb = ApplyOrbitFile(S1_Sub)

    print('Arquivo de órbita: 100%')

    ProductInformation(S1_Sub_Orb)

    S1_Sub_Orb_Cal = Calibration(S1_Sub_Orb, 'Intensity_VH', 'VH')

    print('Imagem calibrada: 100%')

    S1_Sub_Orb_Cal_Ter = Terrain_Correction(S1_Sub_Orb_Cal, 'Sigma0_VH')

    print('Correção Geométrica: 100%')

    S1_Sub_Orb_Cal_Ter_Spk = SpeckleFilter(S1_Sub_Orb_Cal_Ter, 'Sigma0_VH', 'Lee', 3, 3)

    print('Filtragem Speckle: 100%')

    S1_Sub_Orb_Cal_Ter_Spk_dB = Convert_to_dB(S1_Sub_Orb_Cal_Ter_Spk, 'Sigma0_VH')

    print('Conversão para dB: 100%')

    #print('Salvando imagem...')

    #ProductIO.writeProduct(S1_Sub_Orb_Cal_Ter_Spk_dB, 'C:/Users/jales/Desktop/S1/S1A_vscode', 'ENVI')

    #print('Imagem salva com sucesso')
    
    print('Processamento finalizado')

    # ------------------------------------------------------------------------------------------------------

    print('Calculating the histogram...')
    Histogram(S1_Sub_Orb_Cal_Ter_Spk_dB, 'Sigma0_VH_db')
    
    print('Thresholding...')
    find_threshold(histplot[0], histplot[1])
    # ------------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------------