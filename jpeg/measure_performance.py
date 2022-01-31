import requests
from  PIL import Image
import numpy as np
import math
import pandas as pd 
from multiprocessing import Pool
from  jpeg.encoding import *

q_levels = [-55,-45,-35,-10]
n = 700

def sample_entropy(*args):
    url = "https://picsum.photos/512"

    k = args[0]%len(q_levels)

    img = Image.open(requests.get(url, stream=True).raw)
    img = np.array(img)
    
    im_size = img.shape[0]*img.shape[1]

    db_quant = q_levels[k]
    filesize = len(encode(None,None,image=img, db_2_quantization_multiplier=db_quant))
    res = {
        "bits per pixel": filesize/im_size,
        "db_quant": db_quant,
        }



    return res



pool = Pool(4)

d = pool.map(sample_entropy, range(n*len(q_levels)))
pool.close()
pool.join()

d = list(d)
df = pd.DataFrame(data=d)
df.to_csv('data_512.csv',index=False)
