# Runs around an image to identify arcs and crossings.
# Sends back all relevant information to KnotCanvas. TODO: maybe add a parent handler here?

from random import randint
from math import sin, cos, radians
import DrawTools as dtools
import ImageTools as itools

class LineFinder:

    def __init__(self, imageData, displayType='point', x=0, y=0, size=15, degreeRot=0):
        self.imageData = imageData
        self.displayType = displayType
        self.x = x
        self.y = y
        self.size = size
        self.degreeRot = degreeRot

        # movement variables
        self.foundLine = False
        self.stepIter = None # iter object over path to follow

    def setPosition(self, x, y):
        height = self.imageData.shape[0]
        width = self.imageData.shape[1]
        if 0 <= x <= width - 1 and 0 <= y <= height:
            self.x = x
            self.y = y
        else:
            print("Can't set position to ({},{}): out of bounds".format(x, y))

    def setSize(self, size):
        self.size = size

    def setRotation(self, degreeRot):
        self.degreeRot = degreeRot

    # logic to compute where to make next path
    def computeNextPath(self):
        # print('Recomputing path...')
        magnitude = 10

        # continue straight until we've found a line
        if not self.foundLine:
            targetPoint = itools.vectorToPoint(self.x, self.y, magnitude, self.degreeRot)
        else:
            targetPoint = (self.x, self.y)

        path = itools.getPixelsBetween(self.x, self.y, targetPoint[0], targetPoint[1])
        # print('New path (rot {}) goes from {} to {}'.format(self.degreeRot, (self.x, self.y), (targetPoint[0], targetPoint[1])))
        self.stepIter = iter(path) # don't initialize iter to first value

    # update position
    def getNextPosition(self): # TODO: make a tick function and clean this up
        if not self.foundLine:
            # analyze current position and update class variables
            pixelColor = tuple(self.imageData[self.y][self.x][0:3]) # swap x & y, ommit alpha channel
            if pixelColor != (255, 255, 255): # if it's not white
                self.foundLine = True
                print('Found a line at {}'.format((self.x, self.y)))

        if not self.foundLine: # take a standard step on the path
            if self.stepIter is None: # for first run
                self.computeNextPath()
            try:
                nextStep = next(self.stepIter)
            except StopIteration: # ran out of path
                self.computeNextPath() # reset the path
                try:
                    nextStep = next(self.stepIter)
                except StopIteration: # something went wrong
                    print("Error: Couldn't move after path reset")
            except Exception:
                print('Error: Couldn\'t iterate to next step.')
            self.setPosition(nextStep[0], nextStep[1])
            # print('Set position to {}'.format((self.x, self.y)))


    # draw the actual linefinder each tick
    def drawLineFinder(self, qp):
        if self.displayType == 'point':
            qp.drawPoint(self.x, self.y)
        elif self.displayType == 'arrow':
            dtools.drawArrow(qp, self.x, self.y, self.size, self.degreeRot)
        else:
            print('Error: Display type {} not recognized'.format(self.displayType))

