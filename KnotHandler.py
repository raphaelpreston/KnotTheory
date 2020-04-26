from LineFinder import *
from random import randint, choice
from math import sin, cos, radians, sqrt
import DrawTools as dtools
import ImageTools as itools
from ArcHandler import *
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QTimer
from colour import Color
import json

ARC_SEARCH_SHORTCUT = True
ARC_EXPAND_SHORTCUT = True
SPINE_SEARCH_SHORTCUT = True
SPINE_MAP_SHORTCUT = True
SPINE_EXTENSION_SHORTCUT = True

class KnotHandler(): # TODO: delete self variables for certain steps once they're done
    
    def __init__(self, imageData, skelImageData, swapImgFunc):
        
        # image data
        self.imageData = imageData
        self.skelImageData = skelImageData
        self.imageWidth = imageData.shape[1]
        self.imageHeight = imageData.shape[0]

        # callback to swap image being displayed from normal to skeleton
        self.swapImgFunc = swapImgFunc

        # instance variables
        self.status = None
        self.ah = ArcHandler() # TODO: handle coloring too

        # declare for persistence purposes
        self.arcsCompletedInArcExpansion = []
        self.arcsCompletedInSpineMapping = []
        self.currArcInExpansion = 0

    # figure out what to do, status should ONLY be set in this function
    def computeTick(self):

        # start-up
        if self.status is None:
            self.status = "arc-search"
            allPixels = [(col, row) for row in range(0, self.imageHeight)
                    for col in range(0, self.imageWidth)]
            self.pixelIterArcSearch = iter(allPixels)
            self.currPixelInArcSearch = None # don't iter until performTick
            print(self.status)

        # see if we've hit an arc or done searching
        elif self.status == "arc-search":
            # TODO currPix = self.currPixelInArcSearch
            if self.pixelIsArc(self.currPixelInArcSearch): 
                if not self.ah.pixelHasArc(self.currPixelInArcSearch): # doesn't belong to an arc yet
                    self.status = "arc-expand"
                    print("{} at {}".format(self.status, self.currPixelInArcSearch))
                    # initialize BFS expansion
                    self.expansionQueue = [self.currPixelInArcSearch]
                    self.pixelsVisitedInExpansion = set([self.currPixelInArcSearch])
                    self.pixelsToColorInExpansion = [] # color these each step
                    self.boundaryPixelsToColorInExpansion = [self.currPixelInArcSearch]
                    self.ah.addPixelToArc(self.currPixelInArcSearch, self.currArcInExpansion, isBoundary=True)
            # check if we're at the last pixel
            if self.currPixelInArcSearch[0] == self.imageWidth-1 and self.currPixelInArcSearch[1] == self.imageHeight - 1:
                print('Hit last pixel')
                self.status = "spine-search"
                print(self.status)
                self.swapImgFunc() # show skeleton image
                allPixels = [(col, row) for row in range(0, self.imageHeight)
                    for col in range(0, self.imageWidth)]
                self.pixelIterSpineSearch = iter(allPixels)
                self.currPixelInSpineSearch = None # don't iter until performTick()

        # see if we're done expanding in this arc
        elif self.status == "arc-expand":
            if not self.expansionQueue: # we've run out of arc to expand
                self.arcsCompletedInArcExpansion.append(self.currArcInExpansion)
                print('Expanded arc {}'.format(self.currArcInExpansion))
                self.currArcInExpansion += 1
                self.status = "arc-search"
                print(self.status)
                for arcNum in self.arcsCompletedInArcExpansion:
                    print(" - Arc {} has {} pixels.".format(arcNum, len(self.ah.getArcPixels(arcNum))))
                print(" - Total pixels mapped to an arc: {}".format(len(self.ah.getPixelMappings())))

        # see if we hit a spine or done searching
        elif self.status == "spine-search":
            # TODO currPix = self.currPixelInArcSearch
            if self.pixelIsSpine(self.currPixelInSpineSearch): 
                if not self.ah.pixelHasSpine(self.currPixelInArcSearch): # doesn't belong to a spine yet
                    self.status = "spine-map"
                    self.currArcInSpineMap = self.ah.getPixelArc(self.currPixelInSpineSearch)
                    print("{} at {}, belongs to arc {}".format(self.status, self.currPixelInSpineSearch, self.currArcInSpineMap))
                    self.status = "spine-map" # initialize spine mapping
                    print(self.status)
                    self.spineMapQueue = [self.currPixelInSpineSearch]
                    self.pixelsVisitedInSpineMapping = set([self.currPixelInSpineSearch]) # make sure we go away from where we started
                    self.spineMapPosDir = set() # spine pixels that go in the positive direction
                    self.spineMapNegDir = set() # spine pixels that go in the negative direction
            # check if we're at the last pixel
            if self.currPixelInSpineSearch[0] == self.imageWidth-1 and self.currPixelInSpineSearch[1] == self.imageHeight - 1:
                print('Hit last pixel')
                self.status = "spine-extension"
                print(self.status)
                # get paths for all endpoints (make path maximum possible diagonal)
                paths = []
                pathLength = sqrt(self.imageHeight**2 + self.imageWidth **2)
                for arcNum in range(0, self.ah.numArcsInitialized()):
                    paths.extend(self.ah.getPathsForSpineExtension(arcNum, pathLength))
                self.spineExtensionPaths = dict() # endPoint => path excluding endpoint
                self.spineExtensionStepped = dict() # endPoint => steps completed on path
                for path in paths:
                    endPoint = path[0]
                    self.spineExtensionPaths[endPoint] = []
                    self.spineExtensionStepped[endPoint] = []
                    for pixel in path:
                        # make sure pixel' in-bounds and exclude the endPoint
                        if self.pixelInBounds(pixel) and pixel != endPoint:
                            self.spineExtensionPaths[endPoint].append(pixel)

            # map each path pixel to the endpoint and arc to which it belongs
            self.spineExtensionPixelsToArc = dict() # extension pixel => [endPoint, endPoint, ...]
        
        elif self.status == "spine-extension":
            # test to see if all endPoints have intersected
            if self.ah.allEndpointsConnected():
                self.status = "done"
                print(self.status)
            else:
                for pixel, endPoints in self.spineExtensionPixelsToArc.items():
                    if len(endPoints) > 1:
                        if len(endPoints) > 2:
                            print("Error: Multiple lines collided at the same time.")
                            return
                        # ensure we haven't already assigned a connection
                        if (self.ah.getEndPointPair(endPoints[0]) is None
                            and self.ah.getEndPointPair(endPoints[1]) is None):
                            print("Extension lines collided at pixel {}. Endpoints: {}".format(pixel, endPoints))
                            self.ah.connectEndPointToEndPoint(endPoints[0], endPoints[1])
                        # TODO: what happens when if a path hits the wall (aka runs out of path)

        elif self.status == "spine-map":
            if not self.spineMapQueue: # we've run out of spine to map
                # self.ah.setCompleted(self.currArcInExpansion)
                self.arcsCompletedInSpineMapping.append(self.currArcInSpineMap)
                self.status = "spine-search"
                print(self.status)
                # self.ah.printSpineTree(0) # get arc 0's ordered spine
                print('Completed spine {}'.format(self.currArcInSpineMap))
                self.ah.getSpineEndPoints(self.currArcInSpineMap)
                # currArcInSpineMap comes from when we find a pixel that has a
                # spine, so no need to increment it

    # do the stuff that we determined we need to do
    def performTick(self):

        if self.status == "done":
            return

        # move our cursor in the search for arcs
        elif self.status == "arc-search":
            if ARC_SEARCH_SHORTCUT: # cheat and jump until we hit the end or a new arc
                print('Shorcut...')
                while True:
                    thisPixelInSearch = self.currPixelInArcSearch
                    try:
                        self.currPixelInArcSearch = next(self.pixelIterArcSearch)
                        if self.pixelIsArc(self.currPixelInArcSearch):
                            if not self.ah.pixelHasArc(self.currPixelInArcSearch):
                                break # we hit an arc pixel that doesn't belong to an arc
                    except StopIteration:
                        # stay at the last pixel so computeTick knows we're done
                        self.currPixelInArcSearch = thisPixelInSearch
                        break
            else:
                try:
                    self.currPixelInArcSearch = next(self.pixelIterArcSearch)
                except StopIteration:
                    print("Error: We finished iteration in performTick...")
        
        # move our cursor in the search for spines
        elif self.status == "spine-search":
            if SPINE_SEARCH_SHORTCUT: # cheat and jump to closest spine or last pix
                print('Shortcut...')
                while True:
                    thisPixelInSearch = self.currPixelInSpineSearch
                    try:
                        self.currPixelInSpineSearch = next(self.pixelIterSpineSearch)
                        if self.pixelIsSpine(self.currPixelInSpineSearch):
                            if not self.ah.pixelHasSpine(self.currPixelInSpineSearch):
                                break # we hit a spine pixel that doesn't belong to a spine yet
                    except StopIteration:
                        # stay at the last pixel so computeTick knows we're done
                        self.currPixelInSpineSearch = thisPixelInSearch
                        break
            else:
                try:
                    self.currPixelInSpineSearch = next(self.pixelIterSpineSearch)
                except StopIteration:
                    print("Error: We finished iteration in performTick...")
        
        # take one step in all paths
        elif self.status == "spine-extension":

            # take the next step for all paths that haven't intersected yet
            for endPoint, path in self.spineExtensionPaths.items():
                if self.ah.getEndPointPair(endPoint) is None: # not connected
                    # pop the step off
                    nextStep = path.pop(0)

                    # take the step
                    self.spineExtensionStepped[endPoint].append(nextStep)

                    # mark it as an expansion from this arc
                    if nextStep in self.spineExtensionPixelsToArc:
                        self.spineExtensionPixelsToArc[nextStep].append(endPoint)
                    else:
                        self.spineExtensionPixelsToArc[nextStep] = [endPoint]

        
        # take a step in BFS arc expansion
        elif self.status == "arc-expand":
            def arcExpandStep():
                nextPixel = self.expansionQueue.pop(0)
                for n in self.getNeighbors(nextPixel):
                    if self.pixelIsArc(n) and n not in self.pixelsVisitedInExpansion:
                        self.pixelsVisitedInExpansion.add(n) # visit it
                        if self.isBoundaryPixel(n): # figure out what to color it
                            self.boundaryPixelsToColorInExpansion.append(n)
                            self.ah.addPixelToArc(n, self.currArcInExpansion, isBoundary=True)
                        else:
                            self.pixelsToColorInExpansion.append(n) # TODO: handle pixelstocolorinexpansion in AH
                            self.ah.addPixelToArc(n, self.currArcInExpansion)
                        self.expansionQueue.append(n) # add it to the queue
            if ARC_EXPAND_SHORTCUT:
                while(self.expansionQueue):
                    arcExpandStep()
            else:
                arcExpandStep()

        # take a step in spine mapping
        elif self.status == 'spine-map': # TODO: change this expansion and arc expansion to be batch-by-batch, not one at a time (empty whole next ups at once)
            def spineMapStep():
                currPixel = self.spineMapQueue.pop(0)
                # begin by noting this newfound pixel
                self.ah.setPixelAsSpine(currPixel) # assume already in arc
                self.pixelsVisitedInSpineMapping.add(currPixel)
                # get neighbors and error check
                allNeighbors = self.getNeighbors(currPixel)
                neighborsOnSpine = [n for n in allNeighbors if self.pixelIsSpine(n)]
                if len(neighborsOnSpine) > 2 or len(neighborsOnSpine) < 1:
                        print('Error: Pixel {} had more than two or less than one neighbor(s): {}'.format(currPixel, neighborsOnSpine))
                        return
                # initialize directions if necessary (implies no spine pixels are visited yet)
                if len(self.spineMapPosDir) == 0 and len(self.spineMapNegDir) == 0:
                    if len(neighborsOnSpine) == 2:
                        # choose one direction to be positive and one to be negative
                        self.spineMapPosDir.add(neighborsOnSpine[0])
                        self.spineMapNegDir.add(neighborsOnSpine[1])
                    elif len(neighborsOnSpine) == 1:
                        # we must have hit an actual endpoint
                        self.spineMapPosDir.add(neighborsOnSpine[0])
                    for p in neighborsOnSpine:
                        self.spineMapQueue.append(p) # add to queue
                        self.pixelsVisitedInSpineMapping.add(p) # mark as visited
                        self.ah.setPixelAsSpine(p) # assume pixel already in arc
                        # set their neighbors accordingly
                        if p in self.spineMapPosDir:
                            self.ah.setPositionInSpine(currPixel, nxt=p)
                            self.ah.setPositionInSpine(p, prev=currPixel)
                        elif p in self.spineMapNegDir:
                            self.ah.setPositionInSpine(currPixel, prev=p)
                            self.ah.setPositionInSpine(p, nxt=currPixel)
                        else:
                            print("Error: First pixel found on spine wasn't assigned position")
                else: # directions already initialized
                    neighborsInMyDirection = [n for n in neighborsOnSpine
                            if n not in self.pixelsVisitedInSpineMapping]
                    # there might be more than one neighbor (like at a fork)
                    for nextPixel in neighborsInMyDirection:
                        if currPixel in self.spineMapPosDir:
                            self.ah.setPositionInSpine(currPixel, nxt=nextPixel)
                            self.ah.setPositionInSpine(nextPixel, prev=currPixel)
                            # continue in same direction
                            self.spineMapPosDir.add(nextPixel)
                        elif currPixel in self.spineMapNegDir:
                            self.ah.setPositionInSpine(currPixel, prev=nextPixel)
                            self.ah.setPositionInSpine(nextPixel, nxt=currPixel)
                            # continue in same direction
                            self.spineMapNegDir.add(nextPixel)
                        else:
                            print("Error: Pixel {} wasn't assigned a direction in spine mapping".format(currPixel))
                            return
                        # add next pixel to the queue & visited
                        self.spineMapQueue.append(nextPixel)
                        self.pixelsVisitedInSpineMapping.add(nextPixel)
            if SPINE_MAP_SHORTCUT:
                while self.spineMapQueue:
                    spineMapStep()
            else:
                spineMapStep()

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
        if self.status != 'spine-search' and self.status != 'spine-map' and self.status != 'spine-extension' and self.status != 'done':
            pen.setColor(Qt.green)
            qp.setPen(pen)
            for arcNum in self.arcsCompletedInArcExpansion: # all pixels
                for pixel in self.ah.getArcPixels(arcNum):
                    qp.drawPoint(pixel[0], pixel[1])
            pen.setColor(Qt.red)
            qp.setPen(pen)
            for arcNum in self.arcsCompletedInArcExpansion: # boundary pixels
                for pixel in self.ah.getArcPixels(arcNum, boundary=True):
                    qp.drawPoint(pixel[0], pixel[1])
        
        # draw our arc search pixel on top
        if hasattr(self, 'currPixelInArcSearch') and self.currPixelInArcSearch is not None: # first time it'll be None
            pen.setColor(Qt.black)
            qp.setPen(pen)
            qp.drawPoint(self.currPixelInArcSearch[0], self.currPixelInArcSearch[1])
        
        # draw our spine search pixel on top
        if hasattr(self, 'currPixelInSpineSearch') and self.currPixelInSpineSearch is not None:
            pen.setColor(Qt.white)
            qp.setPen(pen)
            qp.drawPoint(self.currPixelInSpineSearch[0], self.currPixelInSpineSearch[1])

        # draw current spine mapping
        if hasattr(self, 'pixelsVisitedInSpineMapping') and self.pixelsVisitedInSpineMapping is not None:
            for pixel in self.pixelsVisitedInSpineMapping:
                pen.setColor(Qt.red)
                qp.setPen(pen)
                qp.drawPoint(pixel[0], pixel[1])
        
        # draw gradient between endpoints of completed spines
        if len(self.arcsCompletedInSpineMapping) > 0:
            for arcNum in self.arcsCompletedInSpineMapping:
                pixels, colors = self.ah.getSpinePaintMap(arcNum)
                for i in range(len(pixels)):
                    pixel = pixels[i]
                    color = colors[i]
                    pen.setColor(QColor(color[0], color[1], color[2]))
                    qp.setPen(pen)
                    qp.drawPoint(pixel[0], pixel[1])
        
        # draw paths extended from endpoints
        if self.status == "spine-extension" or self.status == "done":
            for endPoint, stepped in self.spineExtensionStepped.items():
                for pixel in stepped:
                    if self.ah.getEndPointPair(endPoint) is None:
                        pen.setColor(Qt.white)
                    else:
                        pen.setColor(QColor(50, 205, 50)) # is connected
                    qp.setPen(pen)
                    qp.drawPoint(pixel[0], pixel[1])
        
        if self.status == "done":
            pass
            # for arcNum in self.arcsCompletedInSpineMapping:
            #     print("Heads for arc {}: {}".format(arcNum, self.ah.getSpinePaintMap(arcNum)))
            #     for pixel in self.ah.getSpineEndPoints(arcNum):
            #         pen.setColor(Qt.blue)
            #         qp.setPen(pen)
            #         qp.drawPoint(pixel[0], pixel[1])


    def pixelIsArc(self, pixel):
        row = pixel[1]
        col = pixel[0]
        pixelColor = tuple(self.imageData[row][col][0:3]) # ommit alpha channel
        return pixelColor != (255, 255, 255) # if it's not white
    
    def pixelIsSpine(self, pixel):
        row = pixel[1]
        col = pixel[0]
        pixelWhite = self.skelImageData[row][col] # binary image data
        return pixelWhite

    # get the valid neighbors of a given pixel
    def getNeighbors(self, pixel):
        row = pixel[1]
        col = pixel[0]
        n = []
        for r in [-1, 0, 1]:
            for c in [-1, 0, 1]:
                potentialRow = row+r
                potentialCol = col+c
                if self.pixelInBounds((potentialCol, potentialRow)):
                    potentialPixel = (potentialCol, potentialRow) # swap back
                    if potentialPixel != pixel:
                        n.append(potentialPixel)
        return n
    
    # return true if pixel is in the height and width boundarys
    def pixelInBounds(self, pixel):
        row = pixel[1]
        col = pixel[0]
        return 0 <= row < self.imageHeight and 0 <= col < self.imageWidth

    # determine if a given arc pixel is a boundary of the arc
    def isBoundaryPixel(self, pixel):
        neighbors = self.getNeighbors(pixel)
        neighborColors = []
        for n in neighbors:
            row = n[1]
            col = n[0]
            neighborColors.append(tuple(self.imageData[row][col][0:3])) # ommit alpha channel
        return any([color == (255,255,255) for color in neighborColors])


if __name__ == "__main__":
    from KnotCanvas import main
    main()