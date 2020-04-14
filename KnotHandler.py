from LineFinder import *
from random import randint
from math import sin, cos, radians
import DrawTools as dtools
import ImageTools as itools
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QTimer

ARC_SEARCH_SHORTCUT = True

class KnotHandler():
    
    def __init__(self, imageData):
        
        # image data
        self.imageData = imageData
        self.imageWidth = imageData.shape[1]
        self.imageHeight = imageData.shape[0]

        # instance variables
        self.status = None
        self.arcs = []
        self.crossings = []

        # triggers
        self.currPixelInArcSearch = None # when searching for arcs
        self.doneSearchingForArcs = False # true when done searching for arcs

        # self.lf = LineFinder(self.imageData, x=randint(150,450),
        #     y=randint(150, 450), degreeRot=randint(0,359), displayType='arrow') # initialize LineFinder

    # figure out what to do, status should ONLY be set in this function
    def computeTick(self):

        if self.status is None:
            self.status = "arc-search"
            allPixels = [(col, row) for row in range(0, self.imageHeight)
                    for col in range(0, self.imageWidth)]
            self.pixelIter = iter(allPixels)
            print(self.status)
        
        # see if we've hit an arc
        elif self.status == "arc-search":
            if self.pixelIsArc(self.currPixelInArcSearch):
                self.status = "arc-expand"
                print(self.status)

        elif self.status == "arc-expand":
            pass

        elif self.doneSearchingForArcs: # done searching for arcs
            pass

    # do the stuff that we determined we need to do
    def performTick(self):
        if self.status == "arc-search":
            if ARC_SEARCH_SHORTCUT: # cheat and jump until we hit a dark pixel
                print('Shorcut...')
                while True:
                    try:
                        self.currPixelInArcSearch = next(self.pixelIter)
                        if self.pixelIsArc(self.currPixelInArcSearch):
                            break
                    except StopIteration:
                        self.doneSearchingForArcs = True
                        break
            else:
                try:
                    self.currPixelInArcSearch = next(self.pixelIter)
                except StopIteration:
                    self.doneSearchingForArcs = True

    # draws whatever's necessary when it's time to draw
    def draw(self, qp):
        pen = QPen(Qt.black, 2, Qt.SolidLine)
        qp.setPen(pen)
        if self.currPixelInArcSearch is not None:
            qp.drawPoint(self.currPixelInArcSearch[0], self.currPixelInArcSearch[1])

    def pixelIsArc(self, pixel):
        row = pixel[1]
        col = pixel[0]
        pixelColor = tuple(self.imageData[row][col][0:3]) # ommit alpha channel
        return pixelColor != (255, 255, 255) # if it's not white