from LineFinder import *
from random import randint
from math import sin, cos, radians
import DrawTools as dtools
import ImageTools as itools

class KnotHandler():
    
    def __init__(self, imageData):
        self.imageData = imageData
        self.lf = LineFinder(self.imageData, x=randint(150,450),
            y=randint(150, 450), degreeRot=randint(0,359), displayType='arrow') # initialize LineFinder

    # figure out what to do
    def computeTick(self):
        self.lf.getNextPosition()

    # do the stuff we figured out
    def performTick(self):
        self.lf.setNextPosition()

    # draws whatever's necessary when it's time to draw
    def draw(self, qp):
        self.lf.drawLineFinder(qp) # draw the linefinder