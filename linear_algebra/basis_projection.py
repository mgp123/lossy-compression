from  PIL import Image
import numpy as np
import math
import sys

def get_bitmap(path):
    img = Image.open(path)
    imgArray = np.array(img)
    return imgArray


basis = np.load(sys.argv[1])

basis_dim = int(math.sqrt(basis.shape[0]/3))
print(basis_dim)

path = sys.argv[2]
image = get_bitmap(path)
print(image.shape)
padding = (
    (0,basis_dim-image.shape[0]%basis_dim),
    (basis_dim-image.shape[1]%basis_dim,0),
    (0,0))
image = np.pad(image,
    padding,
    mode="edge"
    )

image = image/255 # normalization is not needed

original_shape = image.shape
print(original_shape)

image = image.reshape(-1,basis.shape[0])
res = basis.T @ image.T 
for i in range(0,res.shape[0],res.shape[0]//180):
    to_save = res
    # 0ing out certain components 
    to_save[:i,:] = 0
    to_save = basis @ to_save
    to_save = to_save.T
    to_save = to_save.reshape(original_shape)
    to_save = to_save[:-padding[0][1], padding[1][0]: ]
    to_save = to_save *255
    to_save = np.clip(to_save, 0, 255) # color may not be in 0.255
    to_save = to_save.astype(np.uint8)
    image = Image.fromarray(to_save) #convert numpy array to image
    path = f'linear_algebra/projection_images/projection_only_{res.shape[0]-i:05d}_components.png'
    image.save(path)




