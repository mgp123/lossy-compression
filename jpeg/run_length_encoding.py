import numpy as np
from jpeg.utils import *
import sys
sys.path.insert(0, '..')

from huffman_codes.huffman import *

def zig_zag_index(nx,ny):
    x = []
    y = []
    current_x = 0
    current_y = 0
    direction = 1
    
    while current_x <nx and current_y <ny:
        x.append(current_x)
        y.append(current_y)

        if (
            (current_x == 0 and direction == -1 and current_y != ny-1) or 
            ( current_x == nx-1 and direction == 1)):
            
            current_y += 1
            direction = -direction
        elif(
            (current_y == 0 and direction == 1) or 
            ( current_y == ny-1 and direction == -1)):
            
            current_x += 1
            direction = -direction

        else:
            current_x+=direction
            current_y-=direction


    return x,y

# adapted from https://stackoverflow.com/a/32681075
def run_length_count(list):
    index = np.where(list[1:] != list[:-1])[0]
    p = np.concatenate([[-1],index,[list.shape[0]-1]])
    values = list[p[1:]]
    p = p[1:] - p[:-1]
    return values, p


# run length encoding by channels given by blocks
# takes a 4d array as input. last two indexes correspond to nxn blocks
# outputs a tuple of lists, first values and second are counts
# the encoding zigzags ACROSS blocks instead of inside the block 
# that is, it jumps through all the values of the same frequency and then changes to a diferent frequency
# (jumping inside blocks seems to be the one that jpeg uses but im not sure)
def run_length_encode(blocks):
    zig_zag_x, zig_zag_y = zig_zag_index(blocks.shape[0],blocks.shape[1])
    flattened = blocks[zig_zag_x,zig_zag_y,:,:,]
    flattened = np.moveaxis(flattened, 0, -1)
    resV =  []
    resC = []
    for i in range(flattened.shape[0]):
        for j in range(flattened.shape[1]):
            v, c = run_length_count(flattened[i,j])
            resV += v.tolist()
            resC += c.tolist()
    return resV,resC

def run_length_decode2(l, blocks_shape):
    nx = 0
    ny = 0
    unroll = [[]]
    cumulative = []
    for v ,c in zip(*l):
        cumulative += [v]*c
        nx += c
        if nx == blocks_shape[0]*blocks_shape[1]:
            nx = 0
            unroll[-1].append(cumulative)
            cumulative = []
            ny += 1
            if ny == blocks_shape[3]:
                unroll.append([])
                ny = 0
    
    if len(unroll[-1]) == 0:
        unroll = unroll[:-1]
    unroll = np.array(unroll)
    unroll =  np.moveaxis(unroll, -1, 0)
    res = np.zeros(blocks_shape)
    zig_zag_x, zig_zag_y = zig_zag_index(blocks_shape[0],blocks_shape[1])
    res[zig_zag_x,zig_zag_y,:,:,] = unroll
    return res

# sligthly faster than run_length_decode2
def run_length_decode(l, blocks_shape):
    unroll = np.repeat(*l)
    unroll = unroll.reshape((blocks_shape[2],blocks_shape[3],-1))
    unroll =  np.moveaxis(unroll, -1, 0)
    res = np.zeros(blocks_shape)
    zig_zag_x, zig_zag_y = zig_zag_index(blocks_shape[0],blocks_shape[1])
    res[zig_zag_x,zig_zag_y,:,:,] = unroll
    return res

def test_run_length_coding(n=4,block_size = 4, verbose=False):
    arr = np.random.randint(16, size=(n,n))
    blocks = array_as_blocks(arr, block_size)

    if verbose:
        print("Using n=",n , " block size= ",block_size )
        print("blocks shape", blocks.shape)

    flattened = run_length_encode(blocks)
    decoded = run_length_decode2(flattened, blocks.shape)
    equal = np.array_equal(blocks,decoded)

    if verbose:
        print("decoded shape",decoded.shape )
        print("equal", equal)

    return equal


def test_multiple_run_length_coding():
    for n in [4,8,16,32,64,128,256,512]:
        print("Testing array",n, "x", n, "...")
        block_sizes = [n]
        while block_sizes[-1] != 2:
            block_sizes.append(block_sizes[-1]//2)

        for block_size in block_sizes:
            for _ in range(10):
                if not test_run_length_coding(n=n,block_size=block_size,verbose=False):
                    print("Failed a test with n=",n," and block_size=", block_size)
                    return False
    print("All tests passed. Yey!")
    return True

