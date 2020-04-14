from LineFinder import *
from random import randint
from math import sin, cos, radians
import DrawTools as dtools
import ImageTools as itools
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QTimer

ARC_SEARCH_SHORTCUT = True
ARC_EXPAND_SHORTCUT = True

class KnotHandler(): # TODO: delete self variables for certain steps once they're done
    
    def __init__(self, imageData):
        
        # image data
        self.imageData = imageData
        self.imageWidth = imageData.shape[1]
        self.imageHeight = imageData.shape[0]

        # instance variables
        self.status = None
        self.numCompletedArcs = 0 # number of arcs fully explored
        self.arcs = [] # index corresponds to pixels in arc
        self.pixelsToArc = dict() # pixels mapped to arc
        self.crossings = []

        # triggers
        self.currPixelInArcSearch = None # when searching for arcs
        self.doneSearchingForArcs = False # true when done searching for arcs

    # figure out what to do, status should ONLY be set in this function
    def computeTick(self):


        # start-up
        if self.status is None:
            self.status = "arc-search"
            allPixels = [(col, row) for row in range(0, self.imageHeight)
                    for col in range(0, self.imageWidth)]
            self.pixelIterArcSearch = iter(allPixels)
            print(self.status)
        
        elif self.doneSearchingForArcs: # done searching for arcs
            if self.status != "done":
                print("done")
            self.status = "done"
        
        # see if we've hit an arc
        elif self.status == "arc-search":
            if self.pixelIsArc(self.currPixelInArcSearch):
                if self.currPixelInArcSearch not in self.pixelsToArc: # doesn't belong to an arc yet
                    self.status = "arc-expand"
                    print("{} at {}".format(self.status, self.currPixelInArcSearch))
                    # initialize expansion
                    self.expansionQueue = [self.currPixelInArcSearch]
                    self.pixelsVisitedInExpansion = set([self.currPixelInArcSearch])
                    self.pixelsToColorInExpansion = [self.currPixelInArcSearch] # color these each step
                    self.currArcInExpansion = self.numCompletedArcs # start at 0
                    self.arcs.append([self.currPixelInArcSearch]) # initialize next arc -> pixel data
                    self.pixelsToArc[self.currPixelInArcSearch] = self.currArcInExpansion

        # see if we're done expanding in this arc
        elif self.status == "arc-expand":
            if not self.expansionQueue: # we've run out of arc to expand
                self.numCompletedArcs += 1
                self.status = "arc-search"
                print(self.status)
                for arcNum in range(0, self.numCompletedArcs):
                    print(" - Arc {} has {} pixels.".format(arcNum, len(self.arcs[arcNum])))
                print(" - Total pixels mapped to an arc: {}".format(len(self.pixelsToArc)))

    # do the stuff that we determined we need to do
    def performTick(self):

        if self.status == "done":
            return

        # move our cursor in the search for arcs
        elif self.status == "arc-search":
            if ARC_SEARCH_SHORTCUT: # cheat and jump until we a new arc
                print('Shorcut...')
                while True:
                    try:
                        self.currPixelInArcSearch = next(self.pixelIterArcSearch)
                        if self.pixelIsArc(self.currPixelInArcSearch):
                            if self.currPixelInArcSearch not in self.pixelsToArc:
                                break
                    except StopIteration:
                        self.doneSearchingForArcs = True
                        break
            else:
                try:
                    self.currPixelInArcSearch = next(self.pixelIterArcSearch)
                except StopIteration:
                    self.doneSearchingForArcs = True
        
        # take a step in BFS
        elif self.status == "arc-expand":
            if ARC_EXPAND_SHORTCUT: # cheat and fill out entire arc at once # TODO: make a function here so don't copy paste code
                while(self.expansionQueue):
                    nextPixel = self.expansionQueue.pop(0)
                    for n in self.getNeighbors(nextPixel):
                        if self.pixelIsArc(n) and n not in self.pixelsVisitedInExpansion:
                            self.pixelsVisitedInExpansion.add(n) # visit it
                            self.pixelsToColorInExpansion.append(n) # mark it for coloring
                            self.expansionQueue.append(n) # add it to the queue
                            self.arcs[self.currArcInExpansion].append(n) # map it under its arc
                            self.pixelsToArc[n] = self.currArcInExpansion # map it to its arc
            else:
                nextPixel = self.expansionQueue.pop(0)
                for n in self.getNeighbors(nextPixel):
                    if self.pixelIsArc(n) and n not in self.pixelsVisitedInExpansion:
                        self.pixelsVisitedInExpansion.add(n) # visit it
                        self.pixelsToColorInExpansion.append(n) # mark it for coloring
                        self.expansionQueue.append(n) # add it to the queue
                        self.arcs[self.currArcInExpansion].append(n) # map it under its arc
                        self.pixelsToArc[n] = self.currArcInExpansion # map it to its arc


    # draws whatever's necessary when it's time to draw
    def draw(self, qp):
        pen = QPen(Qt.black, 1, Qt.SolidLine)
        qp.setPen(pen)

        # draw current arc expansion
        if self.status == "arc-expand":
            pen.setColor(Qt.red)
            qp.setPen(pen)
            for pixel in self.pixelsToColorInExpansion:
                qp.drawPoint(pixel[0], pixel[1])

        # paint completed arcs
        pen.setColor(Qt.green)
        qp.setPen(pen)
        for arcNum in range(0, self.numCompletedArcs):
            for pixel in self.arcs[arcNum]:
                qp.drawPoint(pixel[0], pixel[1])
        
        # draw our search pixel on top
        if self.currPixelInArcSearch is not None: # first time it'll be None
            pen.setColor(Qt.black)
            qp.setPen(pen)
            qp.drawPoint(self.currPixelInArcSearch[0], self.currPixelInArcSearch[1])


    def pixelIsArc(self, pixel):
        row = pixel[1]
        col = pixel[0]
        pixelColor = tuple(self.imageData[row][col][0:3]) # ommit alpha channel
        return pixelColor != (255, 255, 255) # if it's not white

    # get the valid neighbors of a given pixel
    def getNeighbors(self, pixel):
        row = pixel[1]
        col = pixel[0]
        n = []
        for r in [-1, 0, 1]:
            for c in [-1, 0, 1]:
                potentialRow = row+r
                potentialCol = col+c
                if 0 <= potentialRow < self.imageHeight:
                    if 0 <= potentialCol < self.imageWidth:
                        potentialPixel = (potentialCol, potentialRow) # swap back
                        if potentialPixel != pixel:
                            n.append(potentialPixel)
        return n