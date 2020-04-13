# Runs around an image to identify arcs and crossings.
# Sends back all relevant information to KnotCanvas. TODO: maybe add a parent handler here?

from random import randint
import DrawTools as dt

class LineFinder:

    def __init__(self, imageData, displayType='arrow', x=0, y=0, size=0, rot=0):
        self.imageData = imageData
        self.displayType = displayType
        self.x = x
        self.y = y
        self.size = size
        self.rot = rot

    def setPosition(self, x, y):
        # TODO: error test for out of bounds
        self.x = x
        self.y = y

    def setSize(self, size):
        self.size = size

    def setRotation(self, rot):
        self.rot = rot

    def drawLineFinder(self, qp):
        if self.displayType == 'arrow':
            dt.drawArrow(qp, self.x, self.y, self.size, self.rot)
        else:
            print('Error: Display type {} not recognized'.format(self.displayType))

