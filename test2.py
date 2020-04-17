from skimage import img_as_float
from skimage import io, color, morphology
from skimage import io, img_as_uint
import matplotlib.pyplot as plt

image = img_as_float(color.rgb2gray(io.imread('knot.png')))
image_binary = image < 0.5
out_skeletonize = morphology.skeletonize(image_binary)
out_thin = morphology.thin(image_binary)
io.imsave("skeleton.png", img_as_uint(out_skeletonize))
io.imsave("thin.png", img_as_uint(out_thin))


f, (ax0, ax1, ax2) = plt.subplots(1, 3, figsize=(10, 3))

ax0.imshow(image, cmap='gray')
ax0.set_title('Input')

ax1.imshow(out_skeletonize, cmap='gray')
ax1.set_title('Skeletonize')

ax2.imshow(out_thin, cmap='gray')
ax2.set_title('Thin')

plt.savefig('/tmp/knot_out.png')
plt.show()