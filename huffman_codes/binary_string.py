from __future__ import annotations
from typing import Dict, Iterable, List, Tuple

import numpy as np




# internaly we use a list to symbolize the bit stream
# we only convert to real bits when we write to file
class BinaryString:
    def __init__(self, b_string=None):
        self.binary_string = []
        self.cache_str = ""
        if b_string != None:
            self.binary_string = list(str(b_string))
        
        self.update_cache()

    def update_cache(self):
        self.cache_str = "".join(self.binary_string)

    def get_list(self):
        return self.binary_string

    def substring(self, init, end):
        res = BinaryString()
        res.binary_string = self.binary_string[init:end]
        return res


    def append_to_head(self, data):
        self.append(data, to_head=True)
    
    def remove_head(self,n_bits):
        self.binary_string = self.binary_string[n_bits:]
        self.update_cache()

    def append(self,data , to_head=False, check_valid=False):
            bs = None
            try:
                bs = list(str(data)) # may throw error if cant convert to string
            except Exception as error:
                raise ValueError('Could not convert data to string') 

            if to_head:
                self.binary_string = bs+self.binary_string
            else:
                self.binary_string = self.binary_string + bs

            if check_valid and not set(bs).issubset({"0","1"}):
                raise ValueError('String is not binary')
            
            self.update_cache()

    def append_strings(self, *elems: Iterable[BinaryString]):
        for elem in elems:
            self.binary_string = self.binary_string +  list(str(elem))
        self.update_cache()
        return self

    def number_as_binary(n, bits=None):
        res = BinaryString()

        if n==0:
            res.append_to_head(0)

        while n!=0:
            res.append_to_head(n%2)
            n = n//2

        if bits != None and len(res) < bits:
            res.append_to_head("0"*(bits-len(res)))
        elif bits != None and len(res) > bits:
            res.remove_head(len(res)-bits)
        return res
    
    #  overflow if binary string is too big
    def binary_as_number(self) -> int:
        n = 0
        p = len(self)-1
        for c in self.binary_string:
            n += (2**p)* int(c)
            p-=1
        return n

    def signed_number_as_binary(n,bits=None):
        abs_n = abs(n)
        res = BinaryString.number_as_binary(abs_n,bits=bits)
        if n > 0:
            res.append_to_head(0)
        else:
            res.append_to_head(1)
        return res

    def binary_as_signed_number(self) -> int:
        n = BinaryString(self.cache_str[1:]).binary_as_number()
        if self.binary_string[0] == "1":
            n = - n
        return n

    # this idea is a variation of this nice trick for pairing strings from
    #https://math.stackexchange.com/questions/887895/ways-to-code-two-arbitrary-binary-strings-into-one-without-loss-of-information
    def pair_with(self, second_string) -> BinaryString:
        na =  len(self)
        na = BinaryString.number_as_binary(na)
        res = BinaryString("0"*len(na) + "1")
        res = res + na + self + second_string
        return res

    def unpair(self) -> Tuple[BinaryString,BinaryString]:
        i = 0
        while self.binary_string[i] == "0":
            i+=1
        length_na = i
        i+=1
        na = self.binary_string[i:i+length_na]
        na = BinaryString("".join(na))
        na = BinaryString.binary_as_number(na)
        i += length_na
        a = BinaryString("".join(self.binary_string[i:i+na]))
        i += na
        b = BinaryString("".join(self.binary_string[i:]))

        return a, b

    # returns a binary string reprsenting the list of its members, asumes non empty list
    def binary_list_to_binary(ls) -> BinaryString:
        n = len(ls)
        i = n-2
        n = BinaryString.number_as_binary(n)
        res = ls[-1]

        while i >= 0:
            res = ls[i].pair_with(res)
            i-=1

        res = n.pair_with(res)

        return res

    def binary_to_binary_list(self):
        n, tail = self.unpair()
        n = int(n)

        res = []
        for _ in range(n-1):

            element, tail = tail.unpair()
            res.append(element)
        
        res.append(tail)
        
        return res

    def entropy(self,group_by=1) -> int:
        binary_array = np.array(self.binary_string)
        i = 0
        histogram = {}

        for i in range(0, len(self) + 1 - group_by, group_by):
            group = binary_array[i:i+group_by]
            symbol = BinaryString("".join(group))

            histogram[symbol] = histogram.get(symbol, 0) + 1 
        
        return entropy_from_histrogram(histogram)

    def save_to_file(self,path):
        i = 0
        extra_bits = 32-(len(self)+1)%32
        string_to_write = "0"*extra_bits + "1" + str(self)
        buffer = bytearray()

        while i < len(string_to_write):
            number = int(string_to_write[i:i+8], 2)
            buffer.append(number )
            i += 8
        with open(path, 'bw') as f:
            f.write(buffer)
    
    def read_file(path):
        substrings = []
        with open(path, 'rb') as f:
            byte = f.read(4)
            while byte:
                byte_int = int.from_bytes(byte, "big")
                substrings.append(str(BinaryString.number_as_binary(byte_int,bits=32)))
                byte = f.read(4)

        res = BinaryString("".join(substrings))

        i = 0
        while res.binary_string[i] == "0":
            i+=1
        i+=1
        res.remove_head(i)
        return res

    def decode_with_reverse_codebook(self, reverse_codebook:dict, length):
        # the length parameter is needed for the specific case of only one symbol in codebook
        # this would be "" so we need the length just for that situation
        # we could do better than just using the length but a few extra bits wont hurt much

        if len(reverse_codebook) == 1:
            if len(self) != 0:
                raise ValueError("Trying to decode a non empty binary string with a one element codebook would result in an infinite string")
            return [reverse_codebook[""]]*length
        
        else:
            res = []
            seen = ""
            for c in self.binary_string:
                seen += c
                if seen in reverse_codebook:
                    res.append(reverse_codebook[seen])
                    seen = ""

            if seen in reverse_codebook:
                res.append(reverse_codebook[seen])
                seen = ""

            return res




    def __repr__(self) -> str:
        return self.cache_str
    def __str__(self):
        return self.cache_str
    def __len__(self):
        return len(self.binary_string)
    def __int__(self):
        return self.binary_as_number()
    def __add__(self, other)->BinaryString:
       res  = BinaryString() 
       res.binary_string = self.binary_string + other.binary_string
       res.update_cache()
       return res
    def __eq__(self, other) -> bool:
        return str(self.binary_string) == str(other)
    def __hash__(self) -> int:
        return hash(str(self))


def entropy_from_histrogram(histogram:Dict) -> int:
    values  = np.array(list(histogram.values()))
    n = np.sum(values)
    logs = np.log2(values)
    logn = np.log2(n)

    res = 0
    i = 0

    for v in histogram.values():
        res += (v/n) * -(logs[i] - logn)
        i+=1

    return res


def test1():
    numbers= []
    for x in range(32):
        numbers.append(BinaryString.number_as_binary(x))

    for x in numbers:
        print(x)

    print("---------")
    bl = BinaryString.binary_list_to_binary(numbers)
    print(bl)
    print("---------")
    numbers = (bl.binary_to_binary_list())
    for x in numbers:
        print(x)


    sizes = [len(x) for x in numbers]
    print("each individually", sum(sizes))
    print("together", len(bl))

def test2():
    import random
    bit_list= []
    for _ in range(89372):
        bit = random.choice(["0","1"])
        bit_list.append(bit)

    binary = BinaryString()
    binary.binary_string = bit_list
    binary.update_cache()
    
    # print("before saving")
    # print(binary)
    print("-----------")
    binary.save_to_file("temp.mybinary")
    binary_load = BinaryString.read_file("temp.mybinary")
    # print("after saving")
    # print(binary_load)
    # print("-----------")
    print("are they equal:",str(binary) == str(binary_load) )

