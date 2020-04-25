from ImageTools import interpolateToPath


pixels = [(0,0), (1,1), (2,2), (3, 3)]
pixels.reverse()
interpolateToPath(pixels, 10, (0, 0))

# pixels = [(10,10), (11,11), (12,12), (13,13)]
# # pixels.reverse()
# print(interpolateToPath(pixels, 10, (0,0)))

# pixels = [(1,3), (2,4), (4, 4)]
# print(interpolateToPath(pixels, 5, (0,0)))

# TODO: r^2 value is throwing negative values outside of 0 to 1

