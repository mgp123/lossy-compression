from queue import PriorityQueue
from typing import Dict

from huffman_codes.binary_string import  BinaryString

class BinaryTree():
    def __init__(self,value):
        self.value = value
        self.left_tree = None
        self.right_tree = None
    
    def combine(left_tree,right_tree):
        res = BinaryTree(None)
        res.left_tree = left_tree
        res.right_tree = right_tree

        return res
    
    def is_leaf(self):
        return self.left_tree == None and self.right_tree == None

    def get_depth(self):
        if self.is_leaf():
            return 0
        else:
            return max(
                self.left_tree.get_depth(), 
                self.right_tree.get_depth()
                ) + 1

    def to_list(self) -> list :
        n = 2**(self.get_depth()+1) - 2
        res = [None]*(n+1)
        res = self.to_list_aux(1, res)
        return res

    def to_list_aux(self,index,rec):
        rec[index-1] = self.value
        for t,i in [(self.left_tree, 2*index), (self.right_tree, 2*index+1)]:
            if t != None:
                t.to_list_aux(i,rec)
        
        return rec

    def from_list(l:list):
        return BinaryTree.from_list_aux(l,1)

    def from_list_aux(l:list,index):
        if index-1 >= len(l):
            return None
        res =  BinaryTree(l[index-1])
        l_tree = BinaryTree.from_list_aux(l,2*index)
        r_tree = BinaryTree.from_list_aux(l,2*index+1)

        res.left_tree = l_tree
        res.right_tree = r_tree
        return res

    # for using in priority queue    
    def __lt__(self, other):
        return True

# takes a dict of symbol, to count
def huffman_code(histogram: Dict) -> BinaryTree:

    hist_q = PriorityQueue()
    for key, count in histogram.items():
        hist_q.put((count,BinaryTree(key)))
    
    while not hist_q.qsize() == 1:
        count1, key1 = hist_q.get()
        count2, key2 = hist_q.get()

        merge = None
        if count1 < count2:
            merge = BinaryTree.combine(key1,key2)
        else:
            merge = BinaryTree.combine(key2,key1)
        
        hist_q.put((count1+count2, merge))
    
    _, res = hist_q.get()
    return res

def huffman_code_pair_value_count(v,c) -> BinaryTree:

    histogram = {}
    for key, count in zip(v,c):
        histogram[key] = histogram.get(count, 0) + count
    return huffman_code(histogram)


# binary tree to dict of tuples
def get_codebook(tree: BinaryTree) -> Dict: 
    if tree.value != None:
        return {tree.value:BinaryString()}
    else:
        res = {}
        for t, bit in [(tree.left_tree, "0"), (tree.right_tree, "1")]:
            
            if t != None:
                rec_codebook = get_codebook(t)
                for symbol, code in rec_codebook.items():
                    code.append_to_head(bit)
                    res[symbol] = code
        return res

def test_huff():
    hist = {"a":14, "b":2, "c":18, "d":12, "w":15}
    code = huffman_code(hist)

    for value in code.to_list():
        print(value)

    code = get_codebook(code)
    for key, value in code.items():
        print(key, value)
