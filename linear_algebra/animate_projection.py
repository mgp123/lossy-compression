import os
import imageio

png_dir = "linear_algebra/projection_images"
images = []
for file_name in sorted(os.listdir(png_dir)):
    if file_name.endswith('.png'):
        file_path = os.path.join(png_dir, file_name)
        images.append(imageio.imread(file_path))

for _ in range(48):
    images.append(images[-1])

imageio.mimsave('out.gif', images, fps=24)