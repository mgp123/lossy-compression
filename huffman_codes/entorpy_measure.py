import requests
from  PIL import Image
import numpy as np
import math
import pandas as pd 
from multiprocessing import Pool
from  huffman_codes.encoding import *

def sample_entropy(*args):
    url = "https://picsum.photos/512"

    img = Image.open(requests.get(url, stream=True).raw)
    img = np.array(img)
    header, coded_image, filesize = encoded_image_chunks(img)
    histogram = histogram_from_bitmap(img)
    entropy = entropy_from_histrogram(histogram)
    im_size = img.shape[0]*img.shape[1]

    res = {
        "entropy": entropy, 
        "bits per pixel": filesize/im_size,
        "bits per pixel (no header)":  len(coded_image)/im_size
        }



    return res



pool = Pool(4)
d = pool.map(sample_entropy, range(700))
pool.close()
pool.join()

d = list(d)
df = pd.DataFrame(data=d)
df.to_csv('data_512.csv',index=False)
