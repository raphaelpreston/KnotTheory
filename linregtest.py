from ImageTools import interpolateToPath


pixels = [(0,0), (1,1), (2,2), (3,3)]
# pixels.reverse()
interpolateToPath(pixels, 10, (0,0))

pixels = [(10,10), (11,11), (12,12), (13,13)]
# pixels.reverse()
interpolateToPath(pixels, 10, (0,0))

