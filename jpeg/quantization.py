from jpeg.cosine_transform import *
from jpeg.YCbCr_transform import *
from  PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from jpeg.utils import *

quantization_multilpier=0.1

def get_quantization_multilpier():
    global quantization_multilpier
    return quantization_multilpier

def set_quantization_multilpier(x):
    global quantization_multilpier
    quantization_multilpier = x

# quantization_coeficients taken from https://www.impulseadventure.com/photo/jpeg-quantization.html
# it may not result in the same quantization due to different scaling constants
def get_quantization_matrix(is_luminance):
    if is_luminance:
        return get_quantization_matrix_luminance()
    else: 
        return get_quantization_matrix_chrominance()

def get_quantization_matrix_luminance():
    q = np.genfromtxt('jpeg/quantization_coeficients_luminance.csv', delimiter=' ')
    return q*quantization_multilpier

def get_quantization_matrix_chrominance():
    q = np.genfromtxt('jpeg/quantization_coeficients_chrominance.csv', delimiter=' ')
    return q*quantization_multilpier

def quantize(array,is_luminance):
    q = 1/get_quantization_matrix(is_luminance)
    n = 8  # cant change  this without a new quantization table

    blocks = array_as_blocks(array,n)
    blocks = np.einsum("...ij,ij->...ij", blocks,q)
    blocks = np.rint(blocks)
    res = blocks_as_array(blocks,array.shape)
    return res.astype(int)

# multiplies entryies by quantization matrix in blocks
def expand(array,is_luminance):
    q = get_quantization_matrix(is_luminance)
    blocks = array_as_blocks(array,8)
    blocks = np.einsum("...ij,ij->...ij", blocks,q)
    res = blocks_as_array(blocks,array.shape)
    return res



def get_quantized_image(image, multiplier):
    previous_multiplier = get_quantization_multilpier()
    set_quantization_multilpier(multiplier)
    res = YCbCrTransform(image)

    for k in range(3):
        transform = cosine_transform(res[:,:,k])
        q_transform = expand(quantize(transform,k==0),k==0)
        res[:,:,k] = inverse_cosine_transform(q_transform)

    res = YCbCrInverseTransform(res)
    set_quantization_multilpier(previous_multiplier)
    return res



def plot_quantization_levels(image):
    multipliers = [0.1,0.25]
    n =len(multipliers)
    f, axarr = plt.subplots(1,n,figsize = (4*2*n,3))
    for i in range(n):
        axarr[i].imshow(
            get_quantized_image(image,multipliers[i]), 
            interpolation='none',cmap='gray',aspect='auto')
        axarr[i].axis('off')

    plt.show()
