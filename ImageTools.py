# slope functions adapted from
# https://pythonprogramming.net/how-to-program-best-fit-line-machine-learning-tutorial/

# pixelOnSide adapted from 
# https://math.stackexchange.com/questions/274712/calculate-on-which-side-of-a-straight-line-is-a-given-point-located

from math import sin, cos, radians, degrees, sqrt, atan, isnan, isinf
from statistics import mean
import numpy as np
import json

# implementation of Bresenham's line drawing algorithm to return an
# ordered array of integers from one point to another. Credit Wikipedia.
def getPixelsBetween(x0, y0, x1, y1, inclusive=True):
    # round origin and target to nearest pixel
    x0, y0, x1, y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
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
    if pixels[0] != (x0, y0):
        pixels.reverse()
    
    # return inclusive or exclusive
    if not inclusive:
        return pixels[1:-1]
    else:
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

# returns magnitude and degrees of angle for a line from x0,y0 -> x1,y1
def pointsToVector(x0, y0, x1, y1):
    changeInX = float(x1-x0)
    changeInY = float(y1-y0)

    if changeInX == 0 and changeInY == 0: # same point
        return 0, 0

    # get the magnitude
    magnitude = sqrt(changeInX**2 + changeInY**2)

    # get the correct angle in degrees
    if changeInX == 0:
        degreeTheta = 90.0 if y0 < y1 else 270.0
        return magnitude, degreeTheta
    elif changeInY == 0:
        degreeTheta = 0.0 if x0 < x1 else 180.0
        return magnitude, degreeTheta
    else:
        radianTheta = atan(changeInY/changeInX)
        degreeTheta = degrees(radianTheta)
        if x0 < x1 and y0 < y1: # up right
            return magnitude, degreeTheta
        elif x0 < x1 and y0 > y1: # down right
            return magnitude, (360 - abs(degreeTheta)) % 360
        elif x0 > x1 and y0 < y1: # up left
            return magnitude, (180 - abs(degreeTheta)) % 360
        elif x0 > x1 and y0 > y1: # down left:
            return magnitude, (180 + degreeTheta) % 360

# returns the two angles perpendicular to a given angle
def getPerpendicularAngles(degreeTheta):
    degreeTheta = float(degreeTheta)
    return [(degreeTheta - 90.0) % 360, (degreeTheta + 90.0) % 360]

def orderedRange(a, b):
    if a <= b:
        return range(a, b)
    else:
        return range(a, b, -1)

# slope for line of best fit
def slopeFromPoints(points):
    xs = np.array([p[0] for p in points], dtype=np.float64)
    ys = np.array([p[1] for p in points], dtype=np.float64)
    # test to see if we have a vertical slope
    if not any([x != xs[0] for x in xs]): # if all xs are the same
        return float('inf')
    else:
        return (((mean(xs)*mean(ys)) - mean(xs*ys)) /
            ((mean(xs)*mean(xs)) - mean(xs*xs)))

def squared_error(ys_orig, ys_line):
    return sum((ys_line - ys_orig) * (ys_line - ys_orig))

def coefficient_of_determination(ys_orig, ys_line):
    y_mean_line = [mean(ys_orig) for y in ys_orig]
    squared_error_regr = squared_error(ys_orig, ys_line)
    squared_error_y_mean = squared_error(ys_orig, y_mean_line)
    return 1 - (squared_error_regr/squared_error_y_mean)

# get an n-length path of pixels out from fitToPoint such that the n-length path
# follows the best line of fit through points.
# Points must be ordered.
def interpolateToPath(points, n, fitToPoint):
    n = float(n)
    xs = np.array([p[0] for p in points], dtype=np.float64)
    ys = np.array([p[1] for p in points], dtype=np.float64)
    
    # get x0, y0
    x0 = float(fitToPoint[0])
    y0 = float(fitToPoint[1])
    
    # get the slope
    m = slopeFromPoints(points)
    
    # compute the change in x
    changeInX = sqrt((n**2)/(m**2+1))
    
    # compute change in y
    if isinf(m): # vertical slope
        changeInY = n
    else:
        changeInY = m*changeInX
    
    # reverse direction if first point is "less than" the second point
    if isinf(m) and points[-1][1] < points[0][1]:
            changeInX *= -1
            changeInY *= -1
    elif points[-1][0] < points[0][0]:
            changeInX *= -1
            changeInY *= -1

    # compute how well the line fits the original points
    computedYs = [m*x for x in xs]
    r2 = coefficient_of_determination(ys, computedYs)

    # compute destination pixel
    x1 = x0 + changeInX
    y1 = y0 + changeInY

    # get path of pixels to new pixel
    path = getPixelsBetween(x0, y0, x1, y1)

    return path, r2

# return all pixels inside area of rectangle from p1 to p2 with given radius
def getRectangle(p1, p2, radius):
    x1 = p1[0]
    y1 = p1[1]
    x2 = p2[0]
    y2 = p2[1]

    # get the angle from p1 to p2
    _, degreeTheta = pointsToVector(x1, y1, x2, y2)

    # get both angles perpendicular
    perps = getPerpendicularAngles(degreeTheta)

    # for each perpendicular angle, get the corner points of the rectangle
    p1Corners = [vectorToPoint(x1, y1, radius, theta) for theta in perps]
    p2Corners = [vectorToPoint(x2, y2, radius, theta) for theta in perps]

    # print("Corners of the rectangle: {} and {}".format(p1Corners, p2Corners))

    # get the lines of pixels between the corners
    linesLengthwise = [
        getPixelsBetween(p1Corners[0][0], p1Corners[0][1], p2Corners[0][0], p2Corners[0][1]),
        getPixelsBetween(p1Corners[1][0], p1Corners[1][1], p2Corners[1][0], p2Corners[1][1]),
    ]
    linesWidthwise = [
        getPixelsBetween(p1Corners[0][0], p1Corners[0][1], p1Corners[1][0], p1Corners[1][1]),
        getPixelsBetween(p2Corners[0][0], p2Corners[0][1], p2Corners[1][0], p2Corners[1][1])
    ]

    # sort the rectangle into x => {minY: , maxY: } and same for y
    xRange = dict() # min and max for given y
    yRange = dict() # min and max for given x

    boundaryPixels = list(set(linesLengthwise[0] + linesLengthwise[1] + linesWidthwise[0] + linesWidthwise[1]))
    for pixel in boundaryPixels:
        x = pixel[0]
        y = pixel[1]
        if y not in xRange: # test x-range for a given y
            xRange[y] = {"min": x, "max": x}
        else:
            currMin = xRange[y]["min"]
            currMax = xRange[y]["max"]
            if x < currMin:
                xRange[y]["min"] = x
            if x > currMax:
                xRange[y]["max"] = x
        if x not in yRange: # test y-range for a given x
            yRange[x] = {"min": y, "max": y}
        else:
            currMin = yRange[x]["min"]
            currMax = yRange[x]["max"]
            if y < currMin:
                yRange[x]["min"] = y
            if y > currMax:
                yRange[x]["max"] = y
    # print('x range:')
    # print(json.dumps(xRange, indent=2))
    # print('y range:')
    # print(json.dumps(yRange, indent=2))

    # get circumscribed rectangle around corner points
    left = min([p[0] for p in p1Corners + p2Corners])
    right = max([p[0] for p in p1Corners + p2Corners])
    bottom = min([p[1] for p in p1Corners + p2Corners])
    top = max([p[1] for p in p1Corners + p2Corners])

    # print("Circumscribed parent rectangle:")
    # print(" - left: {}".format(left))
    # print(" - right: {}".format(right))
    # print(" - bottom: {}".format(bottom))
    # print(" - top: {}".format(top))


    # determine which of the circumscribed pixels lie inside the rectangle
    areaPixels = set()
    for x in range(left, right + 1):
        for y in range(bottom, top + 1):
            xMin, xMax = xRange[y]["min"], xRange[y]["max"]
            yMin, yMax = yRange[x]["min"], yRange[x]["max"]
            if xMin <= x <= xMax and yMin <= y <= yMax:
                areaPixels.add((x, y))
    
    # print("Pixels in rectangle: {}".format(areaPixels))
    return areaPixels


# return "left" or "right" depending on which side of imaginary line between
# p1 and p2 that pixel is on. returns None if it's on the line
def pixelOnSide(p1, p2, pixel):
    x, y = pixel
    x1, y1 = p1
    x2, y2 = p2
    x, y, x1, y1, x2, y2 = float(x), float(y), float(x1), float(y1), float(x2), float(y2)
    d = (x-x1)*(y2-y1) - (y-y1)*(x2-x1)
    if d < 0:
        return "right" # standard graph would be left
    elif d > 0:
        return "left"
    else:
        return None