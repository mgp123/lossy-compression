from  PIL import Image
import numpy as np
from huffman_codes.codebook import *
from huffman_codes.huffman import *
from huffman_codes.binary_string import *

def histogram_from_bitmap(bitmap):
    histogram = {}
    for i in range(bitmap.shape[0]):
        for j in range(bitmap.shape[1]):
            color = bitmap[i,j]
            color =(color[0], color[1], color[2])
            histogram[color] = histogram.get(color, 0) + 1 
    return histogram

def get_bitmap(path):
    img = Image.open(path)
    imgArray = np.array(img)
    return imgArray

def encode_bitmap(image, codebook) -> BinaryString:
    flat_image = image.view([(f'f{i}',image.dtype) for i in range(image.shape[-1])])[...,0].astype('O')
    coded_image = np.vectorize(codebook.get)(flat_image)
    coded_image = coded_image.flatten()

    coded_image =  map(str,coded_image)
    coded_image = "".join(coded_image)

    return BinaryString(coded_image)



# encodes an image an gives a the tuple of 
# the  header, coded_image and file size
# the first and second are binary strings, 
# the third is the size of the corresponding file
def encoded_image_chunks(image,verbose=False):
    histogram = histogram_from_bitmap(image)
    code = huffman_code(histogram)
    codebook = get_codebook(code)
    coded_image = encode_bitmap(image,codebook)
    code = code.to_list()
    header = colortree_as_binary_string(code)
    im_size_header1 = BinaryString.number_as_binary(image.shape[0])
    im_size_header2 = BinaryString.number_as_binary(image.shape[1])
    im_size_header = im_size_header1.pair_with(im_size_header2)
    header = im_size_header.pair_with(header)

    file_size = len(header)
    file_size += 2*len(BinaryString.number_as_binary(len(header))) + 1
    file_size += len(coded_image)

    if verbose:
        org_size = image.shape[0]*image.shape[1]*24


        print("bits used per pixel:" ,file_size/(image.shape[0]*image.shape[1]))
        print("bits used per pixel (no header):",len(coded_image)/(image.shape[0]*image.shape[1]) )
        print("pixel entropy of original image:", entropy_from_histrogram(histogram))
        print("image size aprox", file_size/(8*1024), "kB")
        print("image size compared to bitmap:" , file_size/org_size)
    

    return header, coded_image, file_size


def encode(path, out_path,verbose=False):
    if verbose:
        print("Encoding", path)

    image = get_bitmap(path)
    header, coded_image, _ = encoded_image_chunks(image,verbose)
    coded_format = header.pair_with(coded_image)
    coded_format.save_to_file(out_path)

def decode(path, out_path, verbose=False):
    if verbose:
        print("Decoding", path)

    binary = BinaryString.read_file(path)
    header, coded_image = binary.unpair()
    imsize, code = header.unpair()
    codebook = decode_binary_string_as_reverse_codebook(code)

    imsize1, imsize2 = imsize.unpair()
    imsize1, imsize2 = BinaryString.binary_as_number(imsize1), BinaryString.binary_as_number(imsize2)
    image = np.zeros((imsize1*imsize2,3), dtype=np.uint8)

    key = ""
    i = 0
    coded_image = str(coded_image)
    for bit in coded_image:
        key += bit
        if key in codebook:
            color = codebook[key]
            image[i,0], image[i,1], image[i,2] = color
            i+=1
            key=""
    
    image = image.reshape((imsize1,imsize2,3))
    image = Image.fromarray(image) #convert numpy array to image
    image.save(out_path)
