from colour import Color
import ImageTools as itools
import json
from random import sample


# number of points to cut off from end of spine for the linear regression
# to make the line that extends out from the tip of the arc
POINTS_TO_CUT = 5

# number of points towards the endpoint to be used for linear regression
POINTS_FOR_LINREG = 20

class ArcHandler:
    def __init__(self):
        self.arcPixels = [] # arcs to pixels (list of sets)
        self.pixelArcs = dict() # pixel to arc
        self.arcBoundaryPixels = [] # arcs to boundary pixels (list of sets)
        self.arcSpinePixels = [] # arcs to spine pixels (list of sets)
        self.pixelSpines = dict() # pixel to spine
        self.spineTrees = [] # for each arc, dict maps pixel => {prev => [], next => []}
        self.spineEndPoints = [] # for each arc, list of endpoints
        self.crossings = [] # arcNum => {endPoint => endPoint (of other arc)}

    # returns a linked list of the entire length of the knot
    def enumerateKnotLength(self):
        # helper function to return next pixel and new direction to travel in
        def nextPixelAndDirKey(currPixel, currDirKey):
            # if no direction, choose one
            if currDirKey is None:
                if self.getNextSpinePixels(currPixel):
                    currDirKey = "next"
                else:
                    currDirKey = "prev"
            # get the next pixels in line
            nextPixels = self._getSpineNeighbors(currPixel, currDirKey)
            # print("Got nextpixels from {}: {}".format(currPixel, nextPixels))
            if len(nextPixels) > 1:
                print("Error: can't have more than 1 neighbor in spine")
                return
            if not nextPixels: # we must be at an endpoint
                epPair = self.getEndPointPair(currPixel)
                # print(" - jumped to {}".format(epPair))
                if epPair is None:
                    print("Error: Pixel {} didn't have an endpoint partner".format(currPixel))
                nextPixels = [epPair]
                # change direction if necessary
                if not self._getSpineNeighbors(epPair, currDirKey):
                    currDirKey = "prev" if currDirKey == "next" else "next"
            return nextPixels[0], currDirKey

        # choose an random spine pixel
        source = sample(self.pixelSpines.keys(), 1)[0]

        # loop through until we hit source again
        nextPixel, currDirKey = nextPixelAndDirKey(source, None)
        enumeration = {source: {"next": nextPixel}}
        currPixel = source
        while nextPixel != source:
            lastPixel = currPixel
            currPixel = nextPixel
            nextPixel, currDirKey = nextPixelAndDirKey(currPixel, currDirKey)
            if currPixel in enumeration:
                print("Error: Overriding pixel {} in enumeration".format(currPixel))
                return
            enumeration[currPixel] = {
                "prev": lastPixel,
                "next": nextPixel
            }
        # nextPixel is now source
        enumeration[source]['prev'] = currPixel
        return enumeration
    
    # returns true if all spine endpoints have pairs
    def allEndpointsConnected(self):
        allEndPoints = []
        for arcNum in range(0, self.numArcsInitialized()):
            allEndPoints.extend(self.getSpineEndPoints(arcNum))
        return not any([self.getEndPointPair(ep) is None for ep in allEndPoints])

    # returns the endpoint that given endpoint is connected to
    # returns None if not connected
    def getEndPointPair(self, ep):
        arcNum = self.getPixelArc(ep)
        if arcNum is None:
            print("Error: endpoint {} was not part of an arc".format(ep))
            return
        if arcNum >= len(self.arcPixels): # not initalized with forceInitialized
            print("Error: Arc {} hasn't been initialized yet")
            return None
        return self.crossings[arcNum].get(ep, None)

    # call this to establish a connection between endpoints
    def connectEndPointToEndPoint(self, ep1, ep2):
        # get the necessary arcs
        arc1 = self.getPixelArc(ep1)
        arc2 = self.getPixelArc(ep2)
        if arc1 is None:
            print("Error: endpoint {} was not part of an arc".format(ep1))
            return
        if arc2 is None:
            print("Error: endpoint {} was not part of an arc".format(ep2))
            return
        
        # establish connection
        if ep1 in self.crossings[arc1] or ep2 in self.crossings[arc2]:
            print("Error: Can't override existing connection.")
        self.crossings[arc1][ep1] = ep2 # connect arc1 to arc2
        self.crossings[arc2][ep2] = ep1 # connect arc2 to arc1

    def numArcsInitialized(self):
        return len(self.arcPixels) # todo: use this function in places change to arcIsInitialized

    # make sure we've allocated space for a new arc
    def forceArcInitialized(self, arcNum):
        i = arcNum
        while i >= len(self.arcPixels): # make sure we've initialized arc
            self.arcPixels.append(set())
            self.arcBoundaryPixels.append(set())
            self.arcSpinePixels.append(set())
            self.spineTrees.append(dict())
            self.spineEndPoints.append(None)
            self.crossings.append(dict())

    # use this to add a pixel to arc or set it as boundary or spine
    def addPixelToArc(self, pixel, arcNum, isBoundary=False, isSpine=False):
        if type(pixel) is not tuple:
            print('Error: Pixel {} must be a tuple. Is {}'.format(pixel, type(pixel)))
            return
        # make sure arc is initialized
        self.forceArcInitialized(arcNum)
        # check if we are overriding
        if pixel in self.pixelArcs and self.pixelArcs[pixel] != arcNum:
            print('Warning: Reassigning pixel {} from arc {} to arc {}'.format(pixel, self.pixelArcs[pixel], arcNum))
        # add pixel
        self.arcPixels[arcNum].add(pixel)
        self.pixelArcs[pixel] = arcNum
        if isBoundary:
            self.setPixelAsBoundary(pixel)
        if isSpine:
            self.setPixelAsSpine(pixel)
        
    def setPixelAsBoundary(self, pixel):
        arcNum = self.getPixelArc(pixel)
        if arcNum is None:
            print("Error: Pixel {} doesn't have an arc".format(pixel))
        self.forceArcInitialized(arcNum) # ensure initialized
        self.arcBoundaryPixels[arcNum].add(pixel)

    # useful for when finding spines b/c the order in which spines are found
    # isn't necessarily the same order in which the arcs were found
    def setPixelAsSpine(self, pixel):
        arcNum = self.getPixelArc(pixel)
        if arcNum is None:
            print("Error: Pixel {} doesn't have an arc".format(pixel))
        self.forceArcInitialized(arcNum) # ensure initialized
        self.spineEndPoints[arcNum] = None # reset endpoints
        self.arcSpinePixels[arcNum].add(pixel) # arc => pixel
        self.pixelSpines[pixel] = arcNum # pixel => arc

    # set a pixel's relative position in its (implied) arc's spine
    # use this to set initial position in spine or edit it later
    def setPositionInSpine(self, pixel, prev=None, nxt=None):
        arcNum = self.getPixelArc(pixel)
        if arcNum is None:
            print("Error: Pixel {} doesn't have an arc".format(pixel))
        
        # ensure arc is initialized
        self.forceArcInitialized(arcNum)

        # reset endpoints for spine
        self.spineEndPoints[arcNum] = None

        # initialize pixel's position entry if necessary
        arcSpineTree = self.spineTrees[arcNum]
        if pixel not in arcSpineTree:
            arcSpineTree[pixel] = {'prev': [], 'next': []}
        
        # insert all relevent values
        if prev is not None:
            arcSpineTree[pixel]['prev'].append(prev)
        if nxt is not None:
            arcSpineTree[pixel]['next'].append(nxt)

    # return the array of next/prev pixels in a given spine pixel
    # returns None if pixel position not set yet with setPositionInSpine
    # returns [] if next or prev pixels haven't been established
    def _getSpineNeighbors(self, pixel, d):
        if d != "next" and d!= "prev": # dir error checking
            print("Error: Expected 'next' or 'prev', got {}".format(d))
        arcNum = self.getPixelArc(pixel)
        if arcNum is None: # not assigned to an arc
            print("Error: Pixel {} doesn't have an arc".format(pixel))
            return
        if pixel not in self.pixelSpines: # not assigned to a spine
            print("Warning: Pixel {} is not a spine pixel".format(pixel))
        if self.pixelSpines[pixel] != arcNum: # assigned to another spine
            print("Error: Pixel {} is not a spine pixel for arc {}, rather for {}".format(pixel, arcNum, self.pixelSpines[pixel]))
            return
        if arcNum >= len(self.arcPixels): # not initalized with forceInitialized yet
            print("Error: Arc {} hasn't been initialized yet")
            return None
        arcSpineTree = self.spineTrees[arcNum]
        if pixel not in arcSpineTree:
            return None
        # return the correct direction
        return arcSpineTree[pixel][d]

    def getNextSpinePixels(self, pixel):
        return self._getSpineNeighbors(pixel, "next")

    def getPrevSpinePixels(self, pixel):
        return self._getSpineNeighbors(pixel, "prev")

    # returns (dir, dist) pair
    def _distToSpinePixel(self, source, target):
        arcNumSource = self.getPixelArc(source)
        arcNumTarget = self.getPixelArc(target)
        if arcNumSource is None or arcNumTarget: # not assigned to an arc
            print("Error: Pixel {} or {} doesn't have an arc".format(source, target))
            return
        if arcNumSource != arcNumTarget:
            print("Error: Pixels {} and {} are in different arcs".format(source, target))
            return
        arcNum = arcNumSource
        if source not in self.pixelSpines: # not assigned to a spine
            print("Warning: Source {} is not a spine pixel".format(source))
            return
        if target not in self.pixelSpines: # not assigned to a spine
            print("Warning: Target {} is not a spine pixel".format(source))
            return
        if self.pixelSpines[source] != arcNum: # assigned to another spine
            print("Error: Source {} is not a spine pixel for arc {}, rather for {}".format(source, arcNum, self.pixelSpines[source]))
            return
        if self.pixelSpines[target] != arcNum: # assigned to another spine
            print("Error: Target {} is not a spine pixel for arc {}, rather for {}".format(target, arcNum, self.pixelSpines[target]))
            return
        if arcNum >= len(self.arcPixels): # not initalized with forceInitialized yet
            print("Error: Arc {} hasn't been initialized yet")
            return None

        print("Computing distance from {} to {}".format(source, target))
        if source == target:
            return None, 0

        # essentially BFS out in both directions until we explored everywhere
        dirFromSource = None
        nextDir = set()
        prevDir = set() # keep track of directions of pixels
        dist = 0
        q = [source]
        visited = set([source])
        while q: # BFS out in batches at a time
            # empty out a batch
            currPixs = [pix for pix in q]
            q = []
            neighbors = []
            for pix in currPixs:
                # get neighbors of all pixels in the q
                nextPixels = self.getNextSpinePixels(pix)
                prevPixels = self.getPrevSpinePixels(pix)
                # keep track of directionality
                nextDir.update(nextPixels)
                prevDir.update(prevPixels)
                # add all neighbors to be explored
                neighbors.extend(nextPixels + prevPixels)
                # see if we've hit our target
                if pix == target:
                    if dirFromSource is not None:
                        print("Error, found multiple ways to get from {} to {}".format(source, target))
                        return
                    if pix in nextDir:
                        dirFromSource = "next"
                    elif pix in prevDir:
                        dirFromSource = "prev"
                    else:
                        print("Error: No direction found for {}".format(pix))
                        print("nexts: {}".format(nextPixels))
                        print("prevs: {}".format(prevPixels))
                        return
            # explore each neighbor
            for n in neighbors:
                if n not in visited:
                    visited.add(n)
                    q.append(n)
            dist += 1
        
        if dirFromSource is None:
            print("Error: Source {} couldn't reach pixel {}".format(source, target))
            return
        return dirFromSource, dist

    # returns true if spine pixel p1 can reach p2 in given direction
    def _spinePixReachable(self, p1, p2, desiredDir):
        actualDir, dist = self._distToSpinePixel(p1, p2)
        return actualDir == desiredDir

    def getSpineEndPoints(self, arcNum):
        if arcNum is None:
            print("Error: Arcnum is None")
            return
        if arcNum >= len(self.arcPixels): # not initalized with forceInitialized
            print("Error: Arc {} hasn't been initialized yet")
            return
        # if end points were already computed, retreive them
        if self.spineEndPoints[arcNum] is not None:
            return self.spineEndPoints[arcNum]
        # otherwise do the work and save them for later use
        ones = [] # pixels with one neighbor
        twos = [] # pixels with two neighbors
        others = [] # pixels with >2 neighbors
        for pixel, data in self.spineTrees[arcNum].items():
            allNeighbors = data['prev'] + data['next']
            l = len(allNeighbors)
            if l == 1:
                ones.append(pixel)
            elif l == 2:
                twos.append(pixel)
            else:
                others.append(pixel)
        print(' - # pixels w/ one neighbor: {}'.format(len(ones)))
        print(' - # pixels w/ two neighbors: {}'.format(len(twos)))
        if len(others) > 0: # sanity check for skeletonization
            print("Warning: Arc {} has {} pixels with more than two neighbors"
                .format(arcNum, len(others)))
        # save for later use
        self.spineEndPoints[arcNum] = list(ones)
        return ones

    # retusns the spine joints of a given arcNum
    def getSpineJoints(self, arcNum):
        spinePixels = self.getArcPixels(arcNum, spine=True)
        return [p for p in spinePixels
            if len(self._getSpineNeighbors(p, 'prev') + self._getSpineNeighbors(p, 'next')) > 2]

    # return pixels, colors for a spine map in order to display a color
    # gradient in all distinct lines (to show endpoints)
    def getSpinePaintMap(self, arcNum):
        endPoints = self.getSpineEndPoints(arcNum)
        heads = [p for p in endPoints if self._getSpineNeighbors(p, 'next')]
        joints = self.getSpineJoints(arcNum)

        # for a bunch of distinct lines
        if len(joints) == 0: # only one distinct line, only one head
            if len(heads) != 1:
                print("Error: Something's wrong... arc {} had no joints but {} heads".format(arcNum, len(heads)))
                return
            head = heads[0]
            line = [head]
            currPixel = head
            while True:
                nextNeighbors = self._getSpineNeighbors(currPixel, 'next')
                if len(nextNeighbors) == 0: # found endpoint of single line
                    break
                if len(nextNeighbors) > 1: # no joints implies only 1 neighbor
                    print("Error: Something's wrong... arc {} had no joints but pixel {} had {} next neighbors".format(arcNum, currPixel, len(nextNeighbors)))
                    return
                line.append(nextNeighbors[0]) # add to line
                currPixel = nextNeighbors[0]
            
            # line is now an array of pixels from head to tail
            # now, get colors for each pixel accordingly
            red = Color("red")
            colors = list(red.range_to(Color("blue"), len(line)))
            rgbs = [color.rgb for color in colors]
            scaledRgbs = [(r*255, g*255, b*255) for (r, g, b) in rgbs]
            return line, scaledRgbs

        else: # multiple distinct lines joined at each joint
            print("Error: This spine has multiple joints. You didn't code that possibilty in, time to do that!")
            return

    # rid spine of joints so it's only one continuous line
    def cleanSpine(self, arcNum):
        joints = self.getSpineJoints(arcNum)

        print("Spine {} has {} joints".format(arcNum, len(joints)))

        # find two joints that are the furthest apart
        maxDist = 0
        jointPair = []
        for j1 in joints:
            for j2 in joints:
                _, dist = self._distToSpinePixel(j1, j2)
                if dist > maxDist:
                    jointPair = [j1, j2]
                    maxDist = dist
        print('Maximum distance: {}'.format(maxDist))
        print('Joint pair: {}'.format(jointPair))

        # cut off extra spines from all joints
        for joint in joints:
            print("Analyzing joint {}".format(joint))
            mainJ1 = jointPair[0]
            mainJ2 = jointPair[1]

            # by definition, a joint has >1 neighbor in only a single direction
            # because the joint was initially discovered from one direction.
            # only one of these neighbor "paths" should lead to a j1 or j2

            # get the neighbors in the split direction of the joint
            prevNs = self.getPrevSpinePixels(joint)
            nextNs = self.getNextSpinePixels(joint)
            if len(prevNs) > 1 and len(nextNs) > 1:
                print("Something went wrong; {} had multiple neighbors in both directions".format(joint))
                print("Next: {}".format(nextNs))
                print("Prev: {}".format(prevNs))
            elif len(prevNs) > 1:
                multNs = prevNs
                splitDir = "prev"
            elif len(nextNs) > 1:
                multNs = nextNs
                splitDir = "next"
            else:
                print("Error: We called {} a joint but it doesn't have multiple neighbors in a direction".format(joint))
            
            # snip the connection to each neighbor that doesn't lead to a main joint
            # via the correct direction
            toSnip = []
            spineTree = self.spineTrees[arcNum]
            for neighbor in multNs:
                canReachJ1 = self._spinePixReachable(neighbor, mainJ1, splitDir)
                canReachJ2 = self._spinePixReachable(neighbor, mainJ2, splitDir)
                if not (canReachJ1 or canReachJ2): # can't reach either
                    toSnip.append(neighbor)

            print('About to snip {}'.format(toSnip))

            # set correct single neighbor manually
            newNeighbors = [n for n in multNs if n not in toSnip]
            if len(newNeighbors) > 1:
                print("Error. New neighbors is {}, but it should be no more than 1 value".format(newNeighbors))
                return
            spineTree[joint][splitDir] = newNeighbors
            print("Set spinetree[{}][{}] to {}".format(joint, splitDir, newNeighbors))

            # remove all pixels in that direction from pixelSpines and arcSpinePixels
            # TODO: WORKING HERE
            
        
        # reset spine endpoints
        self.spineEndPoints[arcNum] = None



    # print spine tree
    def printSpineTree(self, arcNum):
        print(self.spineTrees[arcNum]) # todo, print ordered tree from an endpoint
        # actually it would be cool to just gradiant the drawing over the spine

    # returns a set of all pixels in an arc
    def getArcPixels(self, arcNum, boundary=False, spine=False):
        if boundary:
            return self.arcBoundaryPixels[arcNum]
        elif spine:
            return self.arcSpinePixels[arcNum]
        else:
            return self.arcPixels[arcNum]

    def getPixelMappings(self):
        return self.pixelArcs

    # returns true if a pixel belongs to an arc
    def pixelHasArc(self, pixel):
        return pixel in self.pixelArcs
    
    # returns the arc number of a given pixel
    def getPixelArc(self, pixel):
        return self.pixelArcs[pixel]
        if self.pixelHasArc(pixel):
            return self.pixelArcs[pixel]
        else:
            return None

    # returns true if a pixel belongs to a spine
    def pixelHasSpine(self, pixel):
        return pixel in self.pixelSpines

    # returns the paths of pixels to extend n length from an arc spine endpoint
    # assumes two endpoints on either end of the arc
    def getPathsForSpineExtension(self, arcNum, n):
        if arcNum >= len(self.arcPixels): # not initalized with forceInitialized
            print("Error: Arc {} hasn't been initialized yet")
            return
        
        # get end points of the spine
        spineEndPoints = self.getSpineEndPoints(arcNum)

        # keep track of the points use for linear regression (for drawing)
        allLinRegPoints = set()

        # keep track of both paths to return
        paths = []

        for ep in spineEndPoints: # for each end point
            # get which endpoint this is
            forwardEnd = len(self.getNextSpinePixels(ep)) == 0
            dirKey = "prev" if forwardEnd else "next"

            # this endpoints points for linear regression
            epLinRegPoints = []

            # iterate into the arc and "chop off" the last couple points
            currPoint = ep
            for _ in range(0, POINTS_TO_CUT):
                nextPoints = self._getSpineNeighbors(currPoint, dirKey)
                if len(nextPoints) > 1:
                    print("Erro: There was more than one neighbor.")
                currPoint = nextPoints[0]
            
            # currPoint is the new endpoint to be used for linreg
            for _ in range(0, POINTS_FOR_LINREG):
                epLinRegPoints.append(currPoint)
                allLinRegPoints.add(currPoint)
                nextPoints = self._getSpineNeighbors(currPoint, dirKey)
                if len(nextPoints) > 1:
                    print("Erro: There was more than one neighbor.")
                currPoint = nextPoints[0]
            
            # get n-length path from the endpoint using the linregpoints
            epLinRegPoints.reverse() # points added in the wrong direction
            path, r2 = itools.interpolateToPath(epLinRegPoints, n, ep)

            paths.append(path)
        # now we have two n-length paths extending out of both endpoints
        return paths








if __name__ == "__main__":
    from KnotCanvas import main
    main()