import requests
from  PIL import Image
import numpy as np
import math
import pandas as pd 
from multiprocessing import Pool


def sample_entropy(*args):
    url = "https://picsum.photos/512"

    img = Image.open(requests.get(url, stream=True).raw)
    # img.show()

    imgArray = np.array(img)
    # imgArray = np.random.randint(low=0,high=256, size=(512,512,3), dtype=np.uint8)

    histogram = {}
    for i in range(imgArray.shape[0]):
        for j in range(imgArray.shape[1]):
            color = imgArray[i,j]
            color = color[0], color[1], color[2]
            histogram[color] = histogram.get(color, 0) + 1 

    entropy = 0
    im_size = imgArray.shape[0]*imgArray.shape[1]

    for f in histogram.values():
        entropy += - (f/im_size) * (math.log2(f) - math.log2(im_size))

    return entropy, len(histogram)/im_size



pool = Pool(18)
res = pool.map(sample_entropy, range(500))
pool.close()
pool.join()

entropies, colors = zip(*res)
d = {'entropy': entropies, 'color fraction': colors}
df = pd.DataFrame(data=d)
df.to_csv('data.csv')
