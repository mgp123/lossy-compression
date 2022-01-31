import numpy as np
from PIL import Image
img = np.random.randint(low=0,high=256, size=(300,300,3), dtype=np.uint8)
im = Image.fromarray(img) 
im.save('random.png')