import numpy as np
from numpy.random.mtrand import sample
from scipy.stats import ortho_group 
import matplotlib.pyplot as plt

width = 32
height = 32
channels = 3

m = ortho_group.rvs(dim=width*height*channels)
np.save("basis"+str(height)+"x"+str(width), m)
