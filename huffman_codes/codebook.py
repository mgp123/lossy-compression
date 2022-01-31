from numpy.core.shape_base import _accumulate
from huffman_codes.huffman import get_codebook, huffman_code, BinaryTree
from huffman_codes.binary_string import BinaryString


def color_to_string(r,g,b) -> BinaryString:
    rb = BinaryString.number_as_binary(r, bits=8)
    gb = BinaryString.number_as_binary(g, bits=8)
    bb = BinaryString.number_as_binary(b, bits=8)

    str_rgb = BinaryString()
    str_rgb.append_strings(rb,gb,bb)

    return str_rgb





# takes a list representing a binary tree whose values are tuple r,g,b
def colortree_as_binary_string(l:list) -> BinaryString:
    # here None empty value is goint to be a 24 bit
    # this is the coding that we are going to use
    #   "00" prefix indicates a 10 bits index signaling certain amounts of None
    #   "01" prefix indicates a 3 bit  index signaling certain amounts of None
    #   "1" prefix indicates a 24 bits rgb

    b_string = []
    last_non_empty = -1

    for i, c in enumerate(l):
        if c != None:
            distance = i-last_non_empty-1
            b_string += distance_code(distance)
            b_string.append("1")
            color_string = color_to_string(*c)
            color_string = str(color_string)
            b_string.append(color_string)
            last_non_empty = i
    
    return BinaryString("".join(b_string))


def distance_code(distance) ->str:
    b_string = []
    small_bits=3
    large_bits=10

    if distance < 2**small_bits:
        b_string.append("00")
        distance = BinaryString.number_as_binary(distance,bits=small_bits)
        distance = str(distance)
        b_string.append(distance)
    elif distance < 2**large_bits:
        b_string.append("01")
        distance = BinaryString.number_as_binary(distance,bits=large_bits)
        distance = str(distance)
        b_string.append(distance)
    else:
        dist1, dist_rec = (2**large_bits-1), distance - (2**large_bits-1) 
        b_string = distance_code(dist1) + distance_code(dist_rec)
    return b_string

def decode_binary_string_as_codetree(b_code:BinaryString) -> list:
    res = []
    b_string = b_code.binary_string
    i = 0
    accumulated_distance = 0
    bits_for_distance_code = {"00":3,"01":10}

    non_empty_values = 0
    while i < len(b_string):
        prefix = "".join(b_string[i:i+2])
        if  prefix in bits_for_distance_code:
            bits_distance = bits_for_distance_code[prefix]
            i+=2

            distance = b_string[i:i+bits_distance]
            distance = "".join(distance)
            distance = BinaryString(distance).binary_as_number()
            accumulated_distance += distance
            i+=bits_distance

        else:
            i+=1
            r = BinaryString("".join(b_string[i:i+8]))
            r = r.binary_as_number()
            i+=8
            g = BinaryString("".join(b_string[i:i+8]))
            g = g.binary_as_number()
            i+=8
            b = BinaryString("".join(b_string[i:i+8]))
            b = b.binary_as_number()
            i+=8
            color = (r,g,b)
            res += [None]*accumulated_distance
            accumulated_distance = 0
            non_empty_values +=1
            res.append(color)

    return res

def get_codetree_as_code_tuples(tree:list,rec, index, prefix) -> dict:
    if index  >= len(tree) + 1:
        return

    if tree[index-1] != None:
        rec.append((tree[index-1],prefix))
    else:
        get_codetree_as_code_tuples(tree,rec,2*index, prefix+"0")
        get_codetree_as_code_tuples(tree,rec,2*index+1, prefix+"1")



def decode_binary_string_as_reverse_codebook(b_code:BinaryString) -> dict:
    codetree = decode_binary_string_as_codetree(b_code)
    codebook = []
    get_codetree_as_code_tuples(codetree,codebook,1,"")

    codebook = {bitcode: color for color, bitcode in codebook}
    return codebook


def test():
    histogram = {(255,8,1):32, (1,255,1):15, (1,1,255):18}
    code =  huffman_code(histogram)
    codebook = get_codebook(code)
    code = code.to_list()
    binary_code = colortree_as_binary_string(code)
    code2 = decode_binary_string_as_codetree(binary_code)

    print(codebook)
    print(code)
    print("----------")
    print(code2)

    print(code == code2)

    print(decode_binary_string_as_reverse_codebook(binary_code))
