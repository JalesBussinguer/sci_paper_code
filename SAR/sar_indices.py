import numpy as np

# Tools

def conv2d(matrix, window):

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

def rvi_grd_index(VV, VH):

    """
    RVI - Radar Vegetation Index (Dual Polarization)

    Args:
    VV (array) = Vertical-Vertical polarization
    VH (array) = Vertical-Horizontal polarization
    
    Returns:
        RVI (array) 
    """

    rvi = (4 * VH) / (VV + VH)

    return rvi.astype(np.float32)

def dpsvi_index(VV, VH):

    """
    DPSVI - Dual Polarization SAR Vegetation Index

    Bibliographic reference here

    Args:
    VV (array) = Vertical-Vertical polarization
    VH (array) = Vertical-Horizontal polarization
    
    Returns:
        DPSVI (array)
    """

    VV_max = VV.max() # Maybe use a solver to determine this number

    dpsvi = (VH * ((VV_max * VV - VV * VH + VH^2) + (VV_max * VV - VV^2 + VH * VV))) / (np.sqrt(2) * VV)

    return dpsvi.astype(np.float32)

def dpsvim_index(VV, VH):

    """
    DPSVIm - Modified Dual-Pol SAR Vegetation Index

    Args:
    VV (array) = Vertical-Vertical polarization
    VH (array) = Vertical-Horizontal polarization
    
    Returns:
        DPSVIm (array)
    """
    
    dpsvim = ((VV * VV) + (VV * VH)) / np.sqrt(2)

    return dpsvim.astype(np.float32)

# SLC indices    

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

    dop = (np.sqrt(1.0 - (4.0 * c2_det / np.power(c2_trace, 2))))

    sqdiscr = np.sqrt(np.abs(c2_trace * c2_trace - 4 * c2_det))

    lambda1 = (c2_trace + sqdiscr) * 0.5
    lambda2 = (c2_trace - sqdiscr) * 0.5

    beta = np.abs(lambda1 / (lambda1 + lambda2))

    dprvi = np.abs(1 - (dop * beta))

    return dprvi.astype(np.float32)

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

    dop = (np.sqrt(1.0 - (4.0 * c2_det / np.power(c2_trace, 2))))

    prvi = (1 - dop) * c22s

    return prvi.astype(np.float32)

def rvi_slc_index(c11, c22, window_size):

    kernel = np.ones((window_size, window_size), np.float32) / (window_size * window_size)

    c11_T1 = c11
    c22_T1 = c22

    c11_T1r = conv2d(np.real(c11_T1), kernel)
    c11_T1i = conv2d(np.imag(c11_T1), kernel)
    c11s = c11_T1r + 1j * c11_T1i

    c22_T1r = conv2d(np.real(c22_T1), kernel)
    c22_T1i = conv2d(np.imag(c22_T1), kernel)
    c22s = c22_T1r + 1j * c22_T1i
    
    c2_trace = c11s + c22s

    rvi = 4 * c22s / c2_trace

    return rvi.astype(np.float32)
