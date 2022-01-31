from  PIL import Image
import numpy as np
import matplotlib.pyplot as plt

from jpeg.utils import get_bitmap

def YCbCrtransformMatrix():
    return np.array(
        [
            [0.299,0.587,0.114],
            [-0.168736,-0.331264,0.5],
            [0.5,-0.418688,-0.081312]
            ]
        )

def YCbCrTransform(image):
    transform_matrix = YCbCrtransformMatrix()
    res = np.einsum("ijc,kc->ijk",image,transform_matrix)
    res[:,:,1:] += 128
    return res

def YCbCrInverseTransform(image):
    res = np.copy(image)
    res[:,:,1:] -= 128
    transform_matrix = np.linalg.inv(YCbCrtransformMatrix())
    res = np.einsum("ijk,ck->ijc",res,transform_matrix)
    return res.astype(int)
    

# takes mean by groups of sub_n
def subsample(vector,subrate_rows=1,subrate_columns=1):
    original_shape = vector.shape
    res = vector.reshape((-1,subrate_columns))
    res = np.mean(res,axis=1)
    res = res.reshape((original_shape[0],-1))
    if subrate_rows != 1:
        res = subsample(res.transpose(),subrate_columns=subrate_rows).transpose()
    return res

# repeats values to get output shape
def upsample(vector, output_shape):
    valid_shape = (output_shape[0] % vector.shape[0]) == 0 and (output_shape[1]%vector.shape[1]) == 0
    assert valid_shape, "can't upsample to that shape by repeating values"
    r0 = output_shape[0]//vector.shape[0]
    r1 = output_shape[1]//vector.shape[1]
    res = np.repeat(vector, r0, axis=0)
    res = np.repeat(res, r1, axis=1)
    return res


def decompose_image_in_channels(image):
    _, axarr = plt.subplots(1,4,figsize=(8*(4),10))


    trans = YCbCrTransform(image)
    cumulative = np.zeros_like(image)

    for k in range(3):
        index_to_remove = {x for x in range(3)}
        index_to_remove.remove(k)

        v1 = np.copy(trans)
        for i in index_to_remove:
            if i == 0:
                v1[:,:,i] = 0
            else:
                v1[:,:,i] = 128

        inverse = YCbCrInverseTransform(v1)
        cumulative = cumulative + inverse
        
        # this condition is only for displaying,  
        # it increases brightness for the  Cb and Cr, otherwise they would be too dark
        if k != 0: 
            inverse += 128


        axarr[k+1].imshow(inverse,aspect='equal')
        axarr[k+1].axis('off')

    axarr[0].imshow(cumulative,aspect='equal')
    axarr[0].axis('off')

    plt.tight_layout()
    plt.savefig('out.png', bbox_inches='tight',pad_inches = 0)
    plt.show()

