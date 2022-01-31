from  PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from jpeg.YCbCr_transform import *
from jpeg.utils import *

def get_basis(n=8):
    basis = np.arange(n)
    basis = np.pi*(basis+0.5)/n
    basis = np.einsum("k,i->ki", np.arange(n), basis)
    basis = np.cos(basis)/n
    return basis


# applies DCT to blocks of size nxn. Takes a 2d array as input
def cosine_transform(array, n=8):
    valid_shape = (array.shape[0] % n) == 0 and (array.shape[1]%n) == 0
    error_string = "can't make " + str(n)+"x"+str(n) + " blocks with array shape" + str(array.shape)
    assert valid_shape, error_string

    basis = get_basis(n)
    blocks = array_as_blocks(array,n)
    blocks = np.einsum("...ij,ki,lj->...kl", blocks,basis, basis)
    res = blocks_as_array(blocks,array.shape)
    return res




def inverse_cosine_transform(array, n=8):
    valid_shape = (array.shape[0] % n) == 0 and (array.shape[1]%n) == 0
    error_string = "can't make " + str(n)+"x"+str(n) + " blocks with array shape" + str(array.shape)
    assert valid_shape, error_string    
    
    basis = n*get_basis(n)
    basis[0,:] = 1/2

    blocks = array_as_blocks(array,n)
    blocks =  np.einsum("...ij,ik,jl->...kl", blocks,basis, basis)

    res = 4 * blocks_as_array(blocks,array.shape)

    return res

def decompose_array_in_cosine_basis(array, n=8):
    t = cosine_transform(array,n)
    _, axarr = plt.subplots(1,n*n+1,figsize=((2*1.5)*(4),2.5*1.5))
    for i in range(n):
        for j in range(n):

            temp = np.zeros_like(t)
            temp[i::n,j::n] = np.copy(t[i::n,j::n])
            temp = inverse_cosine_transform(temp,n)

            axarr[i*n+j+1].imshow(temp, interpolation='none',cmap='gray',aspect='equal')
            axarr[i*n+j+1].axis('off')

            # im = Image.fromarray(temp+20)
            # if im.mode != 'RGB':
            #     im = im.convert('RGB')
            # im.save("channels/channel."+str(i)+ "." + str(j)+".png")
    axarr[0].imshow(array, interpolation='none',cmap='gray',aspect='equal')
    axarr[0].axis('off')
    plt.tight_layout()
    plt.savefig('cosine_decomposition.png', bbox_inches='tight',pad_inches = 0)
    plt.show()


# decomposition is done by separating the rgb channels. Note that this zeros out all the negative values
def decompose_image_in_cosine_basis(image, n=8):
    t1 = cosine_transform(image[:,:,0],n)
    t2 = cosine_transform(image[:,:,1],n)
    t3 = cosine_transform(image[:,:,2],n)

    f, axarr = plt.subplots(n,n,figsize = (16,16))
    for i in range(n):
        for j in range(n):
            temp = np.zeros_like(image)
            for channel, k in [(t1,0), (t2,1), (t3,2)]:
                temp[i::n,j::n,k] = np.copy(channel[i::n,j::n])
                temp[:,:,k] = inverse_cosine_transform(temp[:,:,k],n)

            axarr[i,j].imshow(temp, interpolation='none', aspect='equal')
            axarr[i,j].axis('off')
            im = Image.fromarray(temp)
            im.save("channels/channel."+str(i)+ "." + str(j)+".png")
    plt.show()
 

def plot_basis(n):
    f, axarr = plt.subplots(n,n,figsize = (8,8))
    for i in range(n):
        for j in range(n):

            elems = np.zeros((n,n))
            elems[i,j] = 1
            i1 = inverse_cosine_transform(elems,n)
            axarr[i,j].imshow(
                i1, 
                 vmin=-3, vmax=3, interpolation='none',cmap='gray',aspect='auto')
            axarr[i,j].axis('off')
    plt.tight_layout()
    plt.show()

