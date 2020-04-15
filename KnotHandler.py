from LineFinder import *
from random import randint, choice
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
        self.arcBoundaryPixels = [] # boundary pixels of the arcs
        self.crossings = []
        self.arcSpines = [] # spines of the arcs
        self.numCompletedArcSpines = 0 # keep track for painting

        # triggers
        self.currPixelInArcSearch = None # when searching for arcs
        self.doneConstricting = False

    # figure out what to do, status should ONLY be set in this function
    def computeTick(self):

        # start-up
        if self.status is None:
            self.status = "arc-search"
            allPixels = [(col, row) for row in range(0, self.imageHeight)
                    for col in range(0, self.imageWidth)]
            self.pixelIterArcSearch = iter(allPixels)
            print(self.status)

        # see if we've hit an arc or done searching
        elif self.status == "arc-search":
            if self.pixelIsArc(self.currPixelInArcSearch):
                if self.currPixelInArcSearch not in self.pixelsToArc: # doesn't belong to an arc yet
                    self.status = "arc-expand"
                    print("{} at {}".format(self.status, self.currPixelInArcSearch))
                    # initialize expansion
                    self.expansionQueue = [self.currPixelInArcSearch]
                    self.pixelsVisitedInExpansion = set([self.currPixelInArcSearch])
                    self.pixelsToColorInExpansion = [] # color these each step
                    self.boundaryPixelsToColorInExpansion = [self.currPixelInArcSearch]
                    self.currArcInExpansion = self.numCompletedArcs # start at 0
                    self.arcs.append([self.currPixelInArcSearch]) # initialize next arc -> pixel data
                    self.arcBoundaryPixels.append([self.currPixelInArcSearch]) # initialize next arc -> boundary pixel data
                    self.pixelsToArc[self.currPixelInArcSearch] = self.currArcInExpansion
            # check if we're at the last pixel
            if self.currPixelInArcSearch[0] == self.imageWidth-1 and self.currPixelInArcSearch[1] == self.imageHeight - 1:
                self.status = "arc-constrict"
                print(self.status)
                self.currArcConstricting = 0 # initialize arc constriction
                self.pixelsVisitedInArcConstrict = list(self.arcBoundaryPixels[self.currArcConstricting]) # visited all boundaries
                self.nextPixelsToConstrict = list(self.arcBoundaryPixels[self.currArcConstricting]) # layer of pixels to shrink inwards

        # check to see if it's time to constrict the next arc
        elif self.status == "arc-constrict":
            if self.doneConstricting:
                print('done constricting this arc')
                self.arcSpines.append(list(self.nextPixelsToConstrict))
                self.numCompletedArcSpines += 1
                print('That arc had {} pixels in its spine'.format(len(self.nextPixelsToConstrict)))
                if self.currArcConstricting == len(self.arcs) - 1: # all arcs constricted
                    self.status = "done"
                    print(self.status)
                else: # reset to next arc
                    self.currArcConstricting += 1
                    self.pixelsVisitedInArcConstrict = list(self.arcBoundaryPixels[self.currArcConstricting]) # visited all boundaries
                    self.nextPixelsToConstrict = list(self.arcBoundaryPixels[self.currArcConstricting]) # layer of pixels to shrink inwards
                    self.doneConstricting = False

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
            if ARC_SEARCH_SHORTCUT: # cheat and jump until we hit the end or a new arc
                print('Shorcut...')
                print(self.currPixelInArcSearch)
                while True:
                    thisPixelInSearch = self.currPixelInArcSearch
                    try:
                        self.currPixelInArcSearch = next(self.pixelIterArcSearch)
                        if self.pixelIsArc(self.currPixelInArcSearch):
                            if self.currPixelInArcSearch not in self.pixelsToArc:
                                break
                    except StopIteration:
                        # stay at the last pixel so computeTick knows we're done
                        self.currPixelInArcSearch = thisPixelInSearch
                        break
            else:
                try:
                    self.currPixelInArcSearch = next(self.pixelIterArcSearch)
                except StopIteration:
                    print("Error: We finished iteration in performTick...")
        
        # take a step in BFS
        elif self.status == "arc-expand":
            if ARC_EXPAND_SHORTCUT: # cheat and fill out entire arc at once # TODO: make a function here so don't copy paste code
                while(self.expansionQueue):
                    nextPixel = self.expansionQueue.pop(0)
                    for n in self.getNeighbors(nextPixel):
                        if self.pixelIsArc(n) and n not in self.pixelsVisitedInExpansion:
                            self.pixelsVisitedInExpansion.add(n) # visit it
                            if self.isBoundaryPixel(n): # figure out what to color it
                                self.boundaryPixelsToColorInExpansion.append(n)
                                self.arcBoundaryPixels[self.currArcInExpansion].append(n) # mark as boundary
                            else:
                                self.pixelsToColorInExpansion.append(n)
                            self.expansionQueue.append(n) # add it to the queue
                            self.arcs[self.currArcInExpansion].append(n) # map it under its arc
                            self.pixelsToArc[n] = self.currArcInExpansion # map it to its arc
            else:
                nextPixel = self.expansionQueue.pop(0)
                for n in self.getNeighbors(nextPixel):
                    if self.pixelIsArc(n) and n not in self.pixelsVisitedInExpansion:
                        self.pixelsVisitedInExpansion.add(n) # visit it
                        if self.isBoundaryPixel(n): # figure out what to color it
                            self.boundaryPixelsToColorInExpansion.append(n)
                            self.arcBoundaryPixels[self.currArcInExpansion].append(n) # mark as boundary
                        else:
                            self.pixelsToColorInExpansion.append(n)
                        self.expansionQueue.append(n) # add it to the queue
                        self.arcs[self.currArcInExpansion].append(n) # map it under its arc
                        self.pixelsToArc[n] = self.currArcInExpansion # map it to its arc
        
        # take a step in BFS to constict an arc
        elif self.status == "arc-constrict":
            toAnalyze = list(self.nextPixelsToConstrict)
            self.nextPixelsToConstrict = []
            x = 0
            for pixel in toAnalyze:
                for n in self.getNeighbors(pixel):
                    if n in self.arcs[self.currArcConstricting]: # in our arc
                        if n not in self.pixelsVisitedInArcConstrict: # not constricted yet
                            self.pixelsVisitedInArcConstrict.append(n) # visit it
                            self.nextPixelsToConstrict.append(n) # part of next layer
            if len(self.nextPixelsToConstrict) == 0: # can't constrict tighter
                self.nextPixelsToConstrict = list(toAnalyze) # at least paint these
                self.doneConstricting = True

    # draws whatever's necessary when it's time to draw
    def draw(self, qp):
        pen = QPen(Qt.black, 1, Qt.SolidLine)
        qp.setPen(pen)

        # draw current arc expansion
        if self.status == "arc-expand":
            pen.setColor(Qt.yellow)
            qp.setPen(pen)
            for pixel in self.pixelsToColorInExpansion:
                qp.drawPoint(pixel[0], pixel[1])
            pen.setColor(Qt.red)
            qp.setPen(pen)
            for pixel in self.boundaryPixelsToColorInExpansion:
                qp.drawPoint(pixel[0], pixel[1])

        # paint completed arcs
        if self.status != "done":
            pen.setColor(Qt.green)
        else:
            pen.setColor(Qt.white)
        qp.setPen(pen)
        for arcNum in range(0, self.numCompletedArcs): # all pixels
            for pixel in self.arcs[arcNum]:
                qp.drawPoint(pixel[0], pixel[1])
        pen.setColor(Qt.red)
        qp.setPen(pen)
        for arcNum in range(0, self.numCompletedArcs): # boundary pixels
            for pixel in self.arcBoundaryPixels[arcNum]:
                qp.drawPoint(pixel[0], pixel[1])

        # draw completed spines
        if self.status != "done":
            pen.setColor(Qt.yellow)
        else:
            pen.setColor(Qt.green)
        qp.setPen(pen)
        for arcNum in range(0, self.numCompletedArcSpines):
            for pixel in self.arcSpines[arcNum]:
                qp.drawPoint(pixel[0], pixel[1])
        
        # draw current arc constriction
        if self.status == "arc-constrict":
            pen.setColor(Qt.black)
            qp.setPen(pen)
            for pixel in self.nextPixelsToConstrict:
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

    # determine if a given arc pixel is a boundary of the arc
    def isBoundaryPixel(self, pixel):
        neighbors = self.getNeighbors(pixel)
        neighborColors = []
        for n in neighbors:
            row = n[1]
            col = n[0]
            neighborColors.append(tuple(self.imageData[row][col][0:3])) # ommit alpha channel
        return any([color == (255,255,255) for color in neighborColors])