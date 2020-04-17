from skimage.morphology import skeletonize
from skimage import io, img_as_uint
from skimage import data
import matplotlib.pyplot as plt
from skimage.color import rgb2gray
from skimage.util import invert
import numpy as np

# Invert the horse image
knot = rgb2gray(io.imread("knot.png"))
image = knot
horse = data.horse()

image = invert(knot)

# perform skeletonization
skeleton = skeletonize(image)
io.imsave("skeleton.png", img_as_uint(skeleton))
# skeleton = image

# display results
fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(8, 4),
                         sharex=True, sharey=True)

ax = axes.ravel()

ax[0].imshow(image, cmap=plt.cm.gray)
ax[0].axis('off')
ax[0].set_title('original', fontsize=20)

ax[1].imshow(skeleton, cmap=plt.cm.gray)
ax[1].axis('off')
ax[1].set_title('skeleton', fontsize=20)

fig.tight_layout()
plt.show()











# import ImageTools as itools
# imageData = io.imread("knot.png")
# print(imageData.shape)
# # allPixels = [item for row in imageData for item in row]
# # allPixels = [imageData[row][col] for row in imageData for col in imageData[row]]
# width = imageData.shape[1]
# height = imageData.shape[0]
# allPixels = [(col, row) for row in range(0, height)
#                         for col in range(0, width)]
# for pixel in allPixels:
#     print(pixel)
# # i = 0
# # for row in imageData:
# #     for item in row:
# #         i += 1
# # print(len(allPixels))

# # for pixel in allPixels:
# #     print(pixel)

# # pixelData = imageData[402][378]
# # print(pixelData)

# # for i in range(0, imageData.shape[1]):
# #     pixelData = imageData[50][i]
# #     tuple1 = tuple(pixelData[0:3])
# #     print(tuple1 == (255, 255, 255))

# # for pixel in itools.getPixelsBetween(1.0, 1.0, 2.0, 10.0):
# #     print(pixel)

# # p0 = (10, 10)
# # p1 = (15, 10)
# # p2 = (15, 15)
# # p3 = (10, 15)
# # p4 = (5, 5)
# # p5 = (5, 10)
# # p6 = (5, 5)



# # p7 = (10, 5)
# # p8 = (15, 5)

# # for point in [p1, p2, p3, p4, p5, p6, p7, p8]:
# #     print('--({},{}) to ({},{})'.format(p0[0], p0[1], point[0], point[1]))
# #     for pixel in itools.getPixelsBetween(p0[0], p0[1], point[0], point[1]):
# #         print(pixel)


# # print('--{} to {}'.format((0, 10), (6, 9)))
# # for pixel in itools.getPixelsBetween(0, 10, 6, 9):
# #     print(pixel)

# # print('--{} to {}'.format((6, 9), (0, 10)))
# # for pixel in itools.getPixelsBetween(6, 9, 0, 10):
# #     print(pixel)