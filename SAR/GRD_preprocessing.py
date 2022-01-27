from snappy import ProductIO
from snappy import HashMap
from snappy import GPF

import geopandas as gpd
from shapely.geometry import Polygon

import os, gc

# EPSG: 3857
proj_3857 = '''PROJCS["WGS 84 / Pseudo-Mercator", GEOGCS["WGS 84", DATUM["World Geodetic System 1984", SPHEROID["WGS 84", 6378137.0, 298.257223563, AUTHORITY["EPSG","7030"]], AUTHORITY["EPSG","6326"]], PRIMEM["Greenwich", 0.0, AUTHORITY["EPSG","8901"]], UNIT["degree", 0.017453292519943295], AXIS["Geodetic longitude", EAST], AXIS["Geodetic latitude", NORTH], AUTHORITY["EPSG","4326"]], PROJECTION["Popular Visualisation Pseudo Mercator", AUTHORITY["EPSG","1024"]], PARAMETER["semi_minor", 6378137.0], PARAMETER["latitude_of_origin", 0.0], PARAMETER["central_meridian", 0.0], PARAMETER["scale_factor", 1.0], PARAMETER["false_easting", 0.0], PARAMETER["false_northing", 0.0], UNIT["m", 1.0], AXIS["Easting", EAST], AXIS["Northing", NORTH], AUTHORITY["EPSG","3857"]]'''

proj_32722 = '''PROJCS["WGS 84 / UTM zone 22S", GEOGCS["WGS 84", DATUM["World Geodetic System 1984", SPHEROID["WGS 84", 6378137.0, 298.257223563, AUTHORITY["EPSG","7030"]], AUTHORITY["EPSG","6326"]], PRIMEM["Greenwich", 0.0, AUTHORITY["EPSG","8901"]], UNIT["degree", 0.017453292519943295], AXIS["Geodetic longitude", EAST], AXIS["Geodetic latitude", NORTH], AUTHORITY["EPSG","4326"]], PROJECTION["Transverse_Mercator", AUTHORITY["EPSG","9807"]], PARAMETER["central_meridian", -51.0], PARAMETER["latitude_of_origin", 0.0], PARAMETER["scale_factor", 0.9996], PARAMETER["false_easting", 500000.0], PARAMETER["false_northing", 10000000.0], UNIT["m", 1.0], AXIS["Easting", EAST], AXIS["Northing", NORTH], AUTHORITY["EPSG","32722"]]'''

def operator_help(operator):

    """
    Operator parameters help - for developers only!

    Shows the parameters of a operator, its default values and a set of other values.

    Args:
    operator (string) = Operator name or alias
    
    Returns:
        Parameter infos of a operator (array)
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

def ApplyOrbitFile(source):

    """
    Orbit Correction Operator

    The orbit state vectors provided in the metadata of a SAR product are generally not accurate and can be refined with the precise orbit files which are available days-to-weeks after the generation of the product.
    The orbit file provides accurate satellite position and velocity information. Based on this information, the orbit state vectors in the abstract metadata of the product are updated.

    Args:
    source (array) = Sentinel-1 product
    
    Returns:
        Orbit corrected image (array)
    """

    parameters = HashMap()

    parameters.put('orbitType', 'Sentinel Precise (Auto Download)') # Orbit type
    parameters.put('polyDegree', '3') # Polynomial Degree
    parameters.put('continueOnFail', 'false') # Stop the code if the orbit metadata can't be found

    return GPF.createProduct('Apply-Orbit-File', parameters, source)

def ThermalNoiseReduction(source):
    
    """
    Thermal Noise Reduction Operator

    Thermal noise correction can be applied to Sentinel-1 Level-1 SLC products as well as Level-1 GRD products which have not already been corrected. 
    The operator can also remove this correction based on the product annotations (i.e. to re-introduce the noise signal that was removed). 
    Product annotations will be updated accordingly to allow for re-application of the correction.

    Args:
    source (array) = Sentinel-1 product
    
    Returns:
        Thermal Noise corrected image (array)
    """

    parameters = HashMap()
    
    parameters.put('selectedPolarisations', 'VH,VV')
    parameters.put('removeThermalNoise', True)

    return GPF.createProduct('c', parameters, source)

def Calibration(source):

    """
    Radiometric Calibration Operator

    The objective of SAR calibration is to provide imagery in which the pixel values can be directly related to the radar backscatter of the scene. 
    Though uncalibrated SAR imagery is sufficient for qualitative use, calibrated SAR images are essential to quantitative use of SAR data.

    This Operator performs different calibrations for Sentinel-1 products deriving the sigma nought images. 
    Optionally gamma nought and beta nought images can also be created.

    Args:
    source (array) = Sentinel-1 product
    
    Returns:
        Calibrated image (array)
    """   

    parameters = HashMap()

    parameters.put('outputSigmaBand', True)
    parameters.put('sourceBands', 'Amplitude_VH,Amplitude_VV')
    parameters.put('selectedPolarisations', 'VH,VV')
    parameters.put('outputImageInComplex', False) # This is for SLC products
    parameters.put('outputImageScaleInDb', False)

    return GPF.createProduct('Calibration', parameters, source)

def SpeckleFilter(source, size_x, size_y):

    """
    Speckle Filter Operator

    SAR images have inherent salt and pepper like texturing called speckles which degrade the quality of the image and make interpretation of features more difficult. 
    Speckles are caused by random constructive and destructive interference of the de-phased but coherent return waves scattered by the elementary scatters within each resolution cell. 
    Speckle noise reduction can be applied either by spatial filtering or multilook processing.

    Filters supported: 'Boxcar', 'Median', 'Frost', 'Gamma Map', 'Lee', 'Refined Lee', 'Lee Sigma', 'IDAN'

    Args:
    source (array) = Sentinel-1 product
    
    Returns:
        Calibrated image (array)
    """ 

    parameters = HashMap()

    parameters.put('sourceBands', 'Sigma0_VH,Sigma0_VV')
    parameters.put('filter', 'Refined Lee')
    parameters.put('filterSizeX', size_x)
    parameters.put('filterSizeY', size_y)

    return GPF.createProduct('Speckle-Filter', parameters, source)

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
    parameters.put('mapProjection', proj_3857)
    parameters.put('pixelSpacingInMeter', 10.0)
    parameters.put('sourceBands', 'Sigma0_VH,Sigma0_VV')

    return GPF.createProduct('Terrain-Correction', parameters, source)

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

    geom = gdf.geometry.buffer(0.0002).unary_union
    bounds = geom.bounds
    bbox = Polygon.from_bounds(*bounds)
    wkt = bbox.wkt

    return wkt

def main():

    # GPF Initialization
    GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()

    # Product initialization
    path = r'E:/GATEC/Projeto_01/Dados/Imagens/SAR'

    outpath = r'E:/GATEC/Projeto_01/Dados/Imagens/SAR/preprocessadas'

    wkt = get_georegion_wkt('E:/GATEC/Projeto_01/Dados/Area_projeto/bbox_faz_cach_4326.GEOJSON')

    if not os.path.exists(outpath):
        os.makedirs(outpath)
    
    for item in os.listdir(path):
        gc.enable()
        gc.collect()

        if item.endswith('.zip'):

            date = item.split('_')[4]

            product = ProductIO.readProduct(path + '/' + item)

            S1_Orb = ApplyOrbitFile(product)

            S1_Orb_NR = ThermalNoiseReduction(S1_Orb)

            S1_Orb_NR_Cal = Calibration(S1_Orb_NR)

            S1_Orb_NR_Cal_Spk = SpeckleFilter(S1_Orb_NR_Cal)

            S1_Orb_NR_Cal_Spk_TC = TerrainCorrection(S1_Orb_NR_Cal_Spk)

            S1_Orb_NR_Cal_Spk_TC_Sub = Subset(S1_Orb_NR_Cal_Spk_TC, wkt=wkt)

            ProductIO.writeProduct(S1_Orb_NR_Cal_Spk_TC_Sub, outpath + '/' + 'S1_Orb_NR_Cal_Spk_Ter_Sub'+'_'+date+'_'+'3857', 'GeoTIFF')

if __name__== "__main__":
    main()