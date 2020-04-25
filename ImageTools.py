from math import sin, cos, radians, sqrt
from statistics import mean
import numpy as np

# implementation of Bresenham's line drawing algorithm to return an
# ordered array of integers from one point to another. Credit Wikipedia.
def getPixelsBetween(x0, y0, x1, y1):
    # round origin and target to nearest pixel
    x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
    pixels = []
    if abs(y1 - y0) < abs(x1 - x0):
        if x0 > x1:
            _getPixelLow(x1, y1, x0, y0, pixels)
        else:
            _getPixelLow(x0, y0, x1, y1, pixels)
    else:
        if y0 > y1:
            _getPixelHigh(x1, y1, x0, y0, pixels)
        else:
            _getPixelHigh(x0, y0, x1, y1, pixels)

    # ensure path goes from (x0,y0) to (x1,y1)
    if pixels[0] == (x0, y0):
        return pixels
    else:
        pixels.reverse()
        return pixels

def _getPixelLow(x0, y0, x1, y1, pixels):
    # print('pixelLow')
    dx = x1 - x0
    dy = y1 - y0
    yi = 1
    if dy < 0:
        yi = -1
        dy = -dy
    D = 2*dy - dx
    y = y0
    # print('Going from {} to {}'.format(x0, x1+1))
    for x in range(x0, x1 + 1):
        pixels.append((int(x), int(y)))
        if D > 0:
            y = y + yi
            D = D - 2*dx
        D = D + 2*dy

def _getPixelHigh(x0, y0, x1, y1, pixels):
    # print('pixelHigh')
    dx = x1 - x0
    dy = y1 - y0
    xi = 1
    if dx < 0:
        xi = -1
        dx = -dx
    D = 2*dx - dy
    x = x0
    for y in range(y0, y1 + 1):
        pixels.append((int(x),int(y)))
        if D > 0:
               x = x + xi
               D = D - 2*dy
        D = D + 2*dx

def vectorToPoint(x0, y0, magnitude, degreeTheta):
    x1 = x0 + magnitude*cos(radians(degreeTheta))
    y1 = y0 + magnitude*sin(radians(degreeTheta))
    return (int(x1), int(y1))

# slope for line of best fit from
# https://pythonprogramming.net/how-to-program-best-fit-line-machine-learning-tutorial/
def slopeFromPoints(points):
    xs = np.array([p[0] for p in points], dtype=np.float64)
    ys = np.array([p[1] for p in points], dtype=np.float64)
    return (((mean(xs)*mean(ys)) - mean(xs*ys)) /
         ((mean(xs)*mean(xs)) - mean(xs*xs)))

# get an n-length path of pixels out from fitToPoint such that the n-length path
# follows the best line of fit through points.
# Points must be ordered.
def interpolateToPath(points, n, fitToPoint):
    n = float(n)
    
    # get x0, y0
    x0 = float(fitToPoint[0])
    y0 = float(fitToPoint[1])

    
    # get the slope
    m = slopeFromPoints(points)
    
    # compute the change in x
    changeInX = sqrt((n**2)/(m**2+1))
    
    # compute change in y
    changeInY = m*changeInX
    
    # get slope of the best fit line through path
    if points[-1][0] < points[0][0]: # ordered in reverse x direction
        changeInX *= -1
        changeInY *= -1

    print("Slope: {}".format(m))
    print("Change in x: {}".format(changeInX))
    print("Change in y: {}".format(changeInY))

    # e destination pixel
    destPixel = (x0 + changeInX, y0 + changeInY)
    print("Destination pixel: {}".format(destPixel))

    # get path of pixels to new pixel