import numpy as np
from PIL import Image 

def get_bitmap(path):
    img = Image.open(path)
    imgArray = np.array(img)

    # repeat black and white images. 
    # this is probably not what we should do if we want to compress b&w images
    if len(imgArray.shape) == 2:
        imgArray =  imgArray[:, :, np.newaxis]
        imgArray = np.repeat(imgArray,3,axis=2)


    # remove alpha if it has one
    if imgArray.shape[2] == 4:
        return imgArray[:,:,:3]

    return imgArray

def array_as_blocks(array,n):
    v_blocks = array.shape[0]//n
    h_blocks =  array.shape[1]//n
    blocks = array.reshape(v_blocks, n, h_blocks, n).swapaxes(1,2)
    return blocks

def blocks_as_array(blocks,shape):
    return blocks.swapaxes(2,1).reshape(shape)