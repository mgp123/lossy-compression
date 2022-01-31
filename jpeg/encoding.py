import numpy as np
from jpeg.quantization import expand, quantize, set_quantization_multilpier
from jpeg.utils import *
from jpeg.run_length_encoding import *
from jpeg.YCbCr_transform import *
from jpeg.cosine_transform import *
import sys
sys.path.insert(0, '..')
from huffman_codes.huffman import *
from huffman_codes.binary_string import *
import matplotlib.pyplot as plt



def get_histogram(l):
    histogram = {}
    for k in l:
        histogram[k] = histogram.get(k, 0) + 1 
    return histogram

# split binary code of number in chunks, a header of k 0s followed by a 1 indicate the amount of chunks
# if 
def encode_number_to_binary_by_chunks(x,chunk_size ):
    b_string = BinaryString.number_as_binary(x)
    head = "0"*(-(len(b_string)//-chunk_size)-1)  + "1"
    chunks = (len(head))*chunk_size
    head += "0"*(chunks-len(b_string) )

    return head + str(b_string)

def decode_binary_to_number_by_chunks(b_string):
    binary_list = b_string
    amount_of_chunks= 0
    while binary_list[amount_of_chunks] != "1":
        amount_of_chunks += 1
    res = "".join(binary_list[amount_of_chunks+1:])
    res = BinaryString(res)
    res = BinaryString.binary_as_number(res)
    return res


def encode_list_of_numbers_by_chunks(l, chunk_size):
    f = lambda x: encode_number_to_binary_by_chunks(x,chunk_size)
    elems = map(f,l)
    res = BinaryString("".join(elems))
    return res

def decode_binary_as_list_of_numbers_by_chunks(b, chunk_size):
    elems = []
    l_chars = b.get_list()
    i = 0
    while i < len(l_chars):
        chunks = 1
        start_of_number = i
        while l_chars[i] == "0":
            i+=1
            chunks+=1

        i += 1
        number_size = chunks*chunk_size
        i += number_size 
        number = l_chars[start_of_number:i]
        number = decode_binary_to_number_by_chunks(number)

        elems.append(number)

    return elems

def codebook_pair_to_binary_string(x):
    v, c = x
    return BinaryString.signed_number_as_binary(v).pair_with(BinaryString(c))

# this decodes in reverse so as to be used by decoding
def binary_string_to_codebook_pair(x:BinaryString):
    v, c = x.unpair()
    return  str(c), BinaryString.binary_as_signed_number(v),

def codebook_to_binary_string(codebook):
    b_strings = list(map(codebook_pair_to_binary_string,codebook.items()))
    return BinaryString.binary_list_to_binary(b_strings)

def binary_string_to_codebook(b_string:BinaryString):
    b_list = BinaryString.binary_to_binary_list(b_string)
    b_list = list(map(binary_string_to_codebook_pair,b_list))
    return dict(b_list)


chunk_size = 2
block_size = 8 

def encode(
    path, out_path,
    db_2_quantization_multiplier=None,
    subsample_coef_rows = 2,
    subsample_coef_columns = 2, 
    verbose=False):

    if verbose:
        print("Encoding", path)

    image = get_bitmap(path)
    
    shape = image.shape
    padding = ((-shape[0]%(8*subsample_coef_rows),0),(-shape[1]%(8*subsample_coef_columns),0),(0,0))
    
    res = encode_list_of_numbers_by_chunks((padding[0][0],padding[1][0]),chunk_size)
    res = res.pair_with(
        encode_list_of_numbers_by_chunks([subsample_coef_rows,subsample_coef_columns],chunk_size)
        )

    res = res.pair_with(BinaryString.signed_number_as_binary(db_2_quantization_multiplier))
    image = np.pad(image, padding, "edge")

    quantization_multiplier = 2**(db_2_quantization_multiplier/10)
    set_quantization_multilpier(quantization_multiplier)

    image = YCbCrTransform(image)

    for channel_index in range(3):
        channel = image[:,:,channel_index]
        
        # dont subsample luminance
        if channel_index != 0:
            channel = subsample(
                channel, 
                subrate_rows=subsample_coef_rows,
                subrate_columns=subsample_coef_columns)
        
        # cosine transfomr and quantize
        t_channel = channel
        t_channel = cosine_transform(channel,n=block_size)
        t_channel = quantize(t_channel,channel_index==0)
        t_channel = array_as_blocks(t_channel, block_size)

        # loseless compression part, 
        coded_channel_values, coded_channel_count = run_length_encode(t_channel)
        histogram = get_histogram(coded_channel_values)
        code = huffman_code(histogram)
        codebook = get_codebook(code)

        # apply codebook to value array
        coded_channel = np.vectorize(codebook.get)(coded_channel_values)
        coded_channel =  map(str,coded_channel)
        coded_channel = "".join(coded_channel)
        coded_channel = BinaryString(coded_channel)
        coded_channel = coded_channel.pair_with(
            encode_list_of_numbers_by_chunks(coded_channel_count,chunk_size))

        # header contains codebook and shapes
        header = BinaryString()

        header = header.pair_with(
            codebook_to_binary_string(codebook)
        )

        header = header.pair_with(
            encode_list_of_numbers_by_chunks(t_channel.shape,chunk_size)
        )
        
        header = header.pair_with(
            encode_list_of_numbers_by_chunks(channel.shape,chunk_size)
        )

        coded_channel = header.pair_with(coded_channel)
        res = res.pair_with(coded_channel)

    image_shape =  encode_list_of_numbers_by_chunks(image.shape,chunk_size)
    res = res.pair_with(
       image_shape
    )
    if verbose:
        shape_x, shape_y = image.shape[0] - padding[0][0], image.shape[1] - padding[1][0]
        print(f'Encoded image uses aprox {len(res)/(8*1024)} kB')
        print(f'This is {len(res)/(shape_y*shape_x)} bits per pixel')
        print(f'This is a ratio of {len(res)/ (24*shape_x*shape_y)} compared to 24 bits per pixel')

    res.save_to_file(out_path)
    return res

def decode(path, out_path, verbose=False):
    if verbose:
        print("Decoding", path)
    
    binary_string = BinaryString.read_file(path)
    binary_string, image_shape = binary_string.unpair()
    image_shape = decode_binary_as_list_of_numbers_by_chunks(image_shape,chunk_size)
    
    image = np.zeros(image_shape)

    # separate header and channels
    c1, c3 = binary_string.unpair()
    c1, c2 = c1.unpair()
    header, c1 = c1.unpair()

    # decode header info
    header, quantization_multiplier = header.unpair()
    quantization_multiplier = quantization_multiplier.binary_as_signed_number()
    quantization_multiplier = 2**(quantization_multiplier/10)
    set_quantization_multilpier(quantization_multiplier)

    padding, subsample_coef = header.unpair()

    padding = decode_binary_as_list_of_numbers_by_chunks(padding,chunk_size)
    subsample_coef_rows, subsample_coef_columns = decode_binary_as_list_of_numbers_by_chunks(subsample_coef, chunk_size)

    for k, p in enumerate([c1,c2,c3]):
        header, main = p.unpair()
        
        header, b_channel_shape = header.unpair()
        b_codebook, b_block_shape = header.unpair()
        _, b_codebook = b_codebook.unpair()

        codebook = binary_string_to_codebook(b_codebook)
        channel_shape = decode_binary_as_list_of_numbers_by_chunks(b_channel_shape,chunk_size)
        block_shape = decode_binary_as_list_of_numbers_by_chunks(b_block_shape,chunk_size)
        
        b_values, b_counts = main.unpair()
        counts = decode_binary_as_list_of_numbers_by_chunks(b_counts,chunk_size)
        values = b_values.decode_with_reverse_codebook(codebook, len(counts))

        coded_channel = run_length_decode((values,counts),block_shape)
        coded_channel = blocks_as_array(coded_channel,channel_shape)
        coded_channel = expand(coded_channel,k==0)
        coded_channel = inverse_cosine_transform(coded_channel,n=block_size)

        if k != 0:
            upsample_shape = coded_channel.shape[0]*subsample_coef_rows, coded_channel.shape[1]*subsample_coef_columns
            coded_channel = upsample(coded_channel,upsample_shape)
        

        image[:,:,k] = coded_channel
    
    image = YCbCrInverseTransform(image)

    # reverse padding
    image = image[padding[0]:,padding[1]:,:]

    image = np.clip(image,0,255)
    image = image.astype(np.uint8)
    image = Image.fromarray(image)
    image.save(out_path)



def encode_and_decode(path_in, **kwargs):
    path_out = path_in.rsplit('.', 1)[0] + "." + str(kwargs["db_2_quantization_multiplier"]) + ".decoded.png"
    verbose = True
    encode(path_in,"temp.myjpeg",**kwargs, verbose=verbose)
    decode("temp.myjpeg", path_out,verbose=verbose)
