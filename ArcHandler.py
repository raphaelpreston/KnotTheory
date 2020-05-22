from colour import Color
import ImageTools as itools
import json
from random import sample


# number of points to cut off from end of spine for the linear regression
# to make the line that extends out from the tip of the arc
POINTS_TO_CUT = 5

# number of points towards the endpoint to be used for linear regression
POINTS_FOR_LINREG = 20

# (traveled, not absolute), length of line created by the pixels on i to get
# handedness of crossing
I_LINE_LEN = 10

class ArcHandler:
    def __init__(self):
        self.arcPixels = [] # arcs to pixels (list of sets)
        self.pixelArcs = dict() # pixel to arc
        self.arcBoundaryPixels = [] # arcs to boundary pixels (list of sets)
        self.arcSpinePixels = [] # arcs to spine pixels (list of sets)
        self.pixelSpines = dict() # pixel to spine
        self.spineTrees = [] # for each arc, dict maps pixel => {prev => [], next => []}
        self.spineEndPoints = [] # for each arc, list of endpoints
        self.snippedSpinePixs = set() # spine pixels that have been snipped off
        self.crossings = [] # arcNum => {endPoint => endPoint (of other arc)}
        self.knotEnumeration = None # spinePixel => {"next": piexl, "prev": pixel}
        self.ijkCrossings = None # crossingNumber => {"i": {arcNum}, "j"..., "k"...}
        self.handedness = [] # "left" or "right"

    # figures out ijkCrossings, handedness. crossing numbers are in a cyclical
    # order. requires that self.knotEnumeration exists
    def getIJKCrossingsAndHandedness(self):
        ijkTuples = [] # tuples of (i,j,k), same order as ijkPoints
        ijkPoints = [] # tuples of (iPoint, jEndPoint, kEp)
        crossingsSeen = set()
        handedness = [] # reset
        # for each arcNum
        for myArcNum, data in enumerate(self.crossings):
            # for each arc it connects to
            for myEp, otherEp in data.items():

                # skip if we've seen it before
                if (myEp, otherEp) in crossingsSeen or \
                        (otherEp, myEp) in crossingsSeen:
                    continue

                crossingsSeen.add((myEp, otherEp))
                otherArcNum = self.getPixelArc(otherEp)

                # figure out which arc is between the endpoints
                # use rectangle because lines might cross without intersecting
                # diagonally
                pixelsBetween = itools.getRectangle(myEp, otherEp, 2)
                spinesBetween = set()
                pixsOnI = set() # keep track of pixels on i's spine btwn j & k
                for pix in pixelsBetween:
                    if self.pixelHasSpine(pix):
                        spineNum = self.getPixelSpine(pix)
                        if spineNum != myArcNum and spineNum != otherArcNum:
                            spinesBetween.add(spineNum)
                            pixsOnI.add(pix)
                if len(spinesBetween) != 1:
                    print("Error: There were more or less than 1 arc between {} and {}".format(myEp, otherEp))
                    print("Arcs: {}".format(spinesBetween))
                    print("Pixels between: {}".format(pixelsBetween))
                    return
                spinesBetween = list(spinesBetween)
                
                # enumerate i, j, and k; crossing numbers assigned arbitrarily
                myEpNext = self.knotEnumeration[myEp]["next"]
                myEpPrev = self.knotEnumeration[myEp]["prev"]
                i = spinesBetween[0]
                if otherEp == myEpNext: # goes from myEp to otherEp
                    j, k = myArcNum, otherArcNum
                    jEp, kEp = myEp, otherEp
                elif otherEp == myEpPrev: # goes from otherEp to myEp
                    k, j = myArcNum, otherArcNum
                    jEp, kEp = otherEp, myEp
                else:
                    print("Error: Supposed EP connection wasn't in any neighbors")
                    return
                
                # get i point between j and k endpoints
                iPoint = pixsOnI.pop() # arbitrary

                # record the i,j,k values and relevent points
                ijkTuples.append((i, j, k))
                ijkPoints.append((iPoint, jEp, kEp))
                
                # figure out handedness
                # form imaginary line on i around the pixels on i between j & k
                

                # traverse both ways down i to form imaginary line
                nextN = self.knotEnumeration[iPoint]["next"]
                prevN = self.knotEnumeration[iPoint]["prev"]
                posLine = [iPoint, nextN]
                negLine = [prevN]
                currPixs = [nextN, prevN]
                done = False
                while not done:
                    nextsUp = []
                    # for each pixel
                    for currPix in currPixs:
                        # get the neighbor in its appropriate direction
                        myDir = "next" if currPix in posLine else "prev"
                        nextN = self.knotEnumeration[currPix][myDir]
                        # add it to the appropriate directional line
                        if myDir == "next":
                            posLine.append(nextN)
                        else:
                            negLine.append(nextN)
                        # check if we've added enough pixels to the line
                        if len(posLine) + len(negLine) == I_LINE_LEN:
                            done = True
                            break
                        nextsUp.append(nextN)
                    currPixs = nextsUp
                
                # line will become last point of neg dir to last of pos
                p1 = negLine[-1]
                p2 = posLine[-1]

                # determine on which side of the line on i lies j
                pixelOnSide = itools.pixelOnSide(p1, p2, jEp)
                if pixelOnSide == None:
                    print("Error: pixel {} is on the line".format(jEp))
                    return
                # appending to handedness does preserve order
                handedness.append(pixelOnSide)
        # convert into ijkCrossings
        ijkCrossings = [] # reset
        for i, j, k in ijkTuples:
            ijkCrossings.append({"i": i, "j": j, "k": k})

        # sort knot crossings directionally
        # for simplicity, record all j points, map j & k points to crossing nums
        allJs = set([jEp for (_, jEp, _) in ijkPoints])
        jEpToCrossingNum = dict()
        kEpToCrossingNum = dict()
        for crossingNum in range(len(ijkPoints)): # for each crossing num
            _, j, k = ijkCrossings[crossingNum]
            _, jEp, kEp = ijkPoints[crossingNum]
            jEpToCrossingNum[jEp] = crossingNum
            kEpToCrossingNum[kEp] = crossingNum
        if len(jEpToCrossingNum) != len(allJs):
            print("Error: Length of all Js differs from jEpToCrossingNum")
            return

        # given a pixel, return closest pixel that is some crossing's 'j' pixel
        # in the "next" direction
        def skipToJ(pix):
            currPix = self.knotEnumeration[pix]['next']
            while currPix not in allJs: # have yet to reach a j pixel
                currPix = self.knotEnumeration[currPix]['next']
            return currPix

        # helper func to set the next crossing to be an existing crossing
        def setNextCrossing(existingCrossNum):
            self.ijkCrossings.append(ijkCrossings[existingCrossNum])
            self.handedness.append(handedness[existingCrossNum])
        
        # travel around knot and record all crossings in order
        self.ijkCrossings = [] # sorted versions
        self.handedness = []
        setNextCrossing(0) # arbitrary beginning
        currCrossing = 0
        while len(self.handedness) < len(handedness):
            # get k of current crossing number
            _, _, currentKEp = ijkPoints[currCrossing]
            # get the crossing number of next crossing
            nextCrossing = jEpToCrossingNum[skipToJ(currentKEp)]
            # add that crossing as the next in line
            setNextCrossing(nextCrossing)
            # proceed
            currCrossing = nextCrossing



    # returns a doubly linked list of the entire length of the knot
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

        # choose the first spine pixel
        source = list(self.pixelSpines.keys())[0]
        # print("Starting at source {}".format(source))

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
            # print("Set {}'s {} to {}".format(currPixel, "prev", lastPixel))
            # print("Set {}'s {} to {}".format(currPixel, "next", nextPixel))
        # nextPixel is now source
        enumeration[source]['prev'] = currPixel
        # print("Finally, set {}'s {} to {}".format(source, "prev", currPixel))

        # error check
        if len(enumeration) != len(self.pixelSpines.keys()):
            print("Error: Enumeration ({}) and pixelSpines ({}) have different lengths".format(
                len(enumeration), len(self.pixelSpines.keys()
            )))
        if any([len(ns) != 2 for pixel, ns in enumeration.items()]):
            print("Error: A pixel doesn't have two neighbors.")
            return
        
        self.knotEnumeration = enumeration
    
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


    def getPixelSpine(self, pixel):
        return self.pixelArcs[pixel]

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
            # print("Set {}'s prev to {}".format(pixel, prev))
            arcSpineTree[pixel]['prev'].append(prev)
        if nxt is not None:
            # print("Set {}'s next to {}".format(pixel, nxt))
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
        else:
            if self.pixelSpines[pixel] != arcNum: # assigned to another spine
                print("Error: Pixel {} is not a spine pixel for arc {}, rather for {}".format(pixel, arcNum, self.pixelSpines[pixel]))
                return
        if arcNum >= len(self.arcPixels): # not initalized with forceInitialized yet
            print("Error: Arc {} hasn't been initialized yet")
            return None
        arcSpineTree = self.spineTrees[arcNum]
        if pixel not in arcSpineTree:
            return None
        # return neighbors from the correct direction
        return arcSpineTree[pixel][d]

    def getNextSpinePixels(self, pixel):
        return self._getSpineNeighbors(pixel, "next")

    def getPrevSpinePixels(self, pixel):
        return self._getSpineNeighbors(pixel, "prev")

    # returns (dir, dist) pair
    def _distToSpinePixel(self, source, target):
        arcNumSource = self.getPixelArc(source)
        arcNumTarget = self.getPixelArc(target)
        if arcNumSource is None or arcNumTarget is None: # not assigned to an arc
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
                    return dirFromSource, dist
            # explore each neighbor
            for n in neighbors:
                if n not in visited:
                    visited.add(n)
                    q.append(n)
            dist += 1
        if dirFromSource is None: # couldn't find
            print("Error: Source {} couldn't reach pixel {}".format(source, target))
            return None, -1

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
        # heads = [p for p in endPoints if self._getSpineNeighbors(p, 'next')]
        joints = self.getSpineJoints(arcNum)


        if len(joints) == 0:
            # choose source endpoint arbitrarily
            sourceEp = endPoints[0]

            # figure out which direction it goes
            prevNs = self.getPrevSpinePixels(sourceEp)
            nextNs = self.getNextSpinePixels(sourceEp) # TODO: getNextSpinePixels should return [] not None
            if len(nextNs) + len(prevNs) != 1:
                print("Error: Chosen source endpoint for paint mapping of arc {} has more or less than 1 neighbor ".format(arcNum))
                return
            if len(nextNs) == 1:
                direc = "next"
            else:
                direc = "prev"
            
            line = [sourceEp]
            currPixel = sourceEp
            while True:
                neighbors = self._getSpineNeighbors(currPixel, direc)
                if len(neighbors) == 0: # found endpoint of single line
                    break
                if len(neighbors) > 1: # no joints implies only 1 neighbor
                    print("Error: Something's wrong... arc {} had no joints but pixel {} had {} next neighbors".format(arcNum, currPixel, len(neighbors)))
                    return
                line.append(neighbors[0]) # add to line
                currPixel = neighbors[0]
            
            # line is now an array of pixels from head to tail
            # now, get colors for each pixel accordingly
            red = Color("red")
            colors = list(red.range_to(Color("blue"), len(line)))
            rgbs = [color.rgb for color in colors]
            scaledRgbs = [(r*255, g*255, b*255) for (r, g, b) in rgbs]
            return line, scaledRgbs

        else: # multiple distinct lines joined at each joint
            print("Error: This spine has multiple joints. Cleaning must have failed!")
            return


    # snip spine from endpoint up to (and potentially including) the first pixel found in lastOnes
    # it's assumed that at no point will we hit a joint that won't incude a pixel
    # in lastOnes. if cutLastOne, the last one found will be killed too.
    def snipSpine(self, ep, lastOnes, visited):
        arcNum = self.getPixelArc(ep)
        if arcNum is None: # not assigned to an arc
            print("Error: Pixel {} doesn't have an arc".format(ep)) # TODO: integrate these errors into the getting functions themselves
            return
        lastSnip = False # set to true if we have to snip exactly one more
        pixsToFix = None # set if we have to glue together two pixels after last snip
        dirToFix = None
        # start snipping
        currPix = ep
        while True:
            print("      Snipping {}".format(currPix))
            prevNs = self.getPrevSpinePixels(currPix)
            nextNs = self.getNextSpinePixels(currPix) # TODO: getNextSpinePixels should return [] not None
            if nextNs is None and prevNs is None:
                neighbors = []
            else:
                neighbors = prevNs + nextNs
            # mark the lastOnes that we've arrived to
            nsInLastOnes = [n for n in neighbors if n in lastOnes]
            if len(neighbors) > 1 and len(nsInLastOnes) == 0 and not lastSnip:
                print("Snipping Error: We found a joint and none of them were in lastOnes, or currPix")
                print("{}: {}... lastOnes: {}... self: {}".format(currPix, neighbors, lastOnes, currPix))
                return
            
            # remove connection to and from all neighbors, and remove self from map
            for n in neighbors:
                if n in prevNs and n in nextNs:
                    print("Error, currPix {} was in both prev and next neighbors".format(currPix))
                    return
                if n in prevNs:
                    dirToMe = "next"
                elif n in nextNs:
                    dirToMe = "prev"
                self.spineTrees[arcNum][n][dirToMe].remove(currPix)
                print("       Removed {} from spineTrees[{}][{}][{}]".format(currPix, arcNum, n, dirToMe))
            del self.spineTrees[arcNum][currPix]
            print('       Deleted {} from spineTrees[{}]'.format(currPix, arcNum))
            
            # delete self from sets of spine pixels
            self.arcSpinePixels[arcNum].remove(currPix)
            print('       Removed {} from arcSpinePixels[{}]'.format(currPix, arcNum))
            del self.pixelSpines[currPix]
            print('       Deleted {} from pixelSpines'.format(currPix))

            # record as snipped pixel
            self.snippedSpinePixs.add(currPix)

            # that was our last snip
            if lastSnip:
                print("       That was our last snip...")
                if pixsToFix is not None:
                    p1, p2 = pixsToFix
                    print("       Gotta glue together {} and {}".format(p1, p2))

                    # reverse dirs in the direction of the spine we already explored
                    neighborInDir = p1 if p1 in visited else p2
                    otherOne = p2 if p1 in visited else p1
                    oppositeDir = "next" if dirToFix == "prev" else "prev"

                    # first deal with the two pixels
                    tempNextNsInMyDir = self._getSpineNeighbors(neighborInDir, dirToFix)
                    print("        Storing temp {} neighbors: {}".format(dirToFix, tempNextNsInMyDir))
                    self.spineTrees[arcNum][neighborInDir][dirToFix] = otherOne
                    print("        Set {}'s {} to {}".format(neighborInDir, dirToFix, otherOne))
                    self.spineTrees[arcNum][otherOne][oppositeDir] = neighborInDir
                    print("        Set {}'s {} to {}".format(otherOne, oppositeDir, neighborInDir))

                    # now traverse to end of visited spine and reverse directions
                    currPix = neighborInDir
                    while tempNextNsInMyDir:
                        if len(tempNextNsInMyDir) > 1:
                            print("Error: There was more than one neighbor when gluing!!!")
                            return
                        nInMyDir = tempNextNsInMyDir[0]
                        tempNextNsInMyDir = self._getSpineNeighbors(nInMyDir, dirToFix)
                        self.spineTrees[arcNum][currPix][oppositeDir] = nInMyDir
                        print("        Set {}'s {} to {}".format(currPix, oppositeDir, nInMyDir))
                        self.spineTrees[arcNum][nInMyDir][dirToFix] = currPix
                        print("        Set {}'s {} to {}".format(nInMyDir, dirToFix, currPix))
                        currPix = nInMyDir
                    # finally, set last pixel to not point to anything
                    self.spineTrees[arcNum][currPix][oppositeDir] = []
                    print("        finally, set {}'s {} to nothing".format(currPix, oppositeDir))

                    print("        Done glueing")
                print("       Done snipping")
                return
            # if we have lastOnes to kill, kill them too then return
            if len(nsInLastOnes) > 0: # we arrived to some lastOnes
                if len(nsInLastOnes) > 1:
                        print("Snipping Error: More than one of currPix {}'s neighbors was a lastone".format(currPix))
                        return
                # determine if we want to cut the last one or not
                # if the potential snippee has two neighbors in one direction,
                # then you're not damaging anything by snipping, so snip and then
                # glue those two neighbors together
                potSnippee = nsInLastOnes[0]
                potSnippeeNextNs = self.getNextSpinePixels(potSnippee)
                potSnippeePrevNs = self.getPrevSpinePixels(potSnippee)
                if len(potSnippeeNextNs) + len(potSnippeePrevNs) == 1:
                    print("       Don't want to cut the last one, that would rupture the line...")
                    print("       Done snipping")
                    return
                elif len(potSnippeeNextNs) == 2:
                    print("       We can snip last one because it has two neighbors in next direction")
                    lastSnip = True
                    currPix = potSnippee
                    pixsToFix = list(potSnippeeNextNs)
                    dirToFix = "next"
                elif len(potSnippeePrevNs) == 2:
                    print("       We can snip last one because it has two neighbors in prev direction")
                    lastSnip = True
                    currPix = potSnippee
                    pixsToFix = list(potSnippeePrevNs)
                    dirToFix = "prev"
            else: # we must have only one neighbor
                currPix = neighbors[0]


    # rid spine of joints so it's only one continuous line
    def cleanSpine(self, arcNum):

        # TODO: move up
        VARIATION_REQUIRED = .25 # if the smaller path is less than 25% smaller

        # intuition here is that for each joint, you want to cut the smaller path, or both.
        # keep a pointer at each end point. shrink towards center step by step.
        # if a pointer hits a joint, wait. when the partner pointer arrives, if
        # the lengths of the two paths are less than VARIATION_OK, kill them both.
        # otherwise, kill only the smaller one. Done when all pointers intersect.
        endpoints = self.getSpineEndPoints(arcNum)

        # step in one from each endpoint, halting if necessary
        # if at a joint, until the other end points catches up
        halting = set()
        q = list(endpoints)
        visited = set(endpoints)
        paths = {ep: [] for ep in endpoints} # paths from each endpoint (and joint, as necessary)
        onPaths = {ep: ep for ep in endpoints} # maps pixel to whichever original pointers path it's on
        while len(q) > 1: # stop when we're left with one pixel or none
            print("Pointers: {}".format(q))
            # inspect batch of pointers
            nextPixs = []
            toVisit = set()
            for pix in q:
                print("  Inspecting {}".format(pix))
                # get all neighbors
                nextNs = self.getNextSpinePixels(pix)
                prevNs = self.getPrevSpinePixels(pix)
                if nextNs is None and prevNs is None:
                    # we must be at a joint and this pointer's path must have been deleted
                    pixNeighbors = []
                else:
                    pixNeighbors = nextNs + prevNs
                newNeighbors = [n for n in pixNeighbors if n not in visited]
                print("    new neighbors: {}".format(newNeighbors))
                print("    all neighbors: {}".format(pixNeighbors))
                # halt if this pixel is a joint
                # if len(newNeighbors) > 1:
                if len(pixNeighbors) > 2: # have to check behind us too
                    halting.add(pix)
                    print("    Halted.")
                # test if another endpoint has reduced down to where we were halting
                # and potentially resume and compare paths
                pixOGPointer = onPaths[pix]
                pixPath = paths[pixOGPointer] # TODO: honestly make a function for this lol
                # look for nearby pointers, or nearby visited pixels not visited by pix
                involvedNeighbors = [n for n in pixNeighbors if n in q or n in visited and n != pixOGPointer and n not in pixPath]
                # involvedNeighbors = [n for n in pixNeighbors if n in q]
                if pix in halting and len(involvedNeighbors) > 0: # TODO: WORKING HERE
                    # pointer neighbors isn't good enough to check. we have to check if any neighbors have been visited at all
                    halting.remove(pix)
                    # since only one pixel in each joint has multiple neighbors,
                    # all but one pointer will be lost because their newNeighbors
                    # will be nothing or the same neighbor will be added twice
                    # this also prevents multiple triggers on the same joint
                    print("    Resumed.")
                    print("    Paths:")
                    # cut relevent paths
                    # compare all paths against each other because
                    # >2-joints possible at double knubs # TODO: TEST THIS
                    pointersToCut = set()
                    allPointersHere = [pix] + involvedNeighbors
                    print("    All the pointers involved here are: {}".format(allPointersHere))
                    for i in range(len(allPointersHere)):
                        pointer1 = allPointersHere[i]
                        for j in range(i+1, len(allPointersHere)):
                            pointer2 = allPointersHere[j]
                            print("      checking pointer {} against {}".format(pointer1, pointer2))
                            p1OGPointer = onPaths[pointer1]
                            p1Path = paths[p1OGPointer]
                            print("     P1's path:")
                            print("      {}: {}".format(p1OGPointer, p1Path))
                            p2OGPointer = onPaths[pointer2]
                            p2Path = paths[p2OGPointer]
                            print("     P2's path:")
                            print("      {}: {}".format(p2OGPointer, p2Path))
                            # determine which path to cut
                            p1Len = len(p1Path)
                            p2Len = len(p2Path) # TODO: restructure these into if statements
                            longerPath = p1Path if p1Len >= p2Len else p2Path
                            shorterPath = p2Path if p1Len >= p2Len else p1Path
                            diff = len(longerPath) - len(shorterPath)
                            percentSmaller = float(diff) / float(len(longerPath))
                            print("     The diff between paths is {}".format(diff))
                            longerP = pointer1 if p1Path == longerPath else pointer2 # ---- for testing -----
                            shorterP = pointer2 if p1Path == longerPath else pointer1
                            print("     That means {}'s path is {} percent shorter than {}'s path".format(shorterP, int(percentSmaller*100), longerP))
                            # if the paths are close enough, snip both
                            destinationPointers = set()
                            if percentSmaller < VARIATION_REQUIRED:
                                pointersToCut.update([p1OGPointer, p2OGPointer])
                                destinationPointers.update([shorterP, longerP]) # analogous to pointer1 and pointer2
                                print("     So, add them both to be snipped")
                            else: # smaller one is assumed to be a knub
                                shorterOGPointer = p2OGPointer if p1Len >= p2Len else p1OGPointer
                                destinationPointers.add(shorterP)
                                pointersToCut.add(shorterOGPointer)
                                print("     So, just add {} to be snipper".format(shorterOGPointer))
                    print("    After all that, here's whats going to be snipped: {}, until we hit anything in heree: {}".format(pointersToCut, destinationPointers))
                    # snip everything from OG pointers up to and including pointers involved with joint
                    for oGPointer in pointersToCut:
                        # cut all the way if it's an even split, otherwise
                        # it's a knub, so leave the last one in (initially)
                        cutLastOne = len(pointersToCut) > 1
                        # use closest existing pixel to oGPointer on path
                        # this way, if there was already a joint further down
                        # one of the paths, it's effectively removed to because
                        # we start deleting from the joint
                        pathCopy = list(paths[oGPointer])
                        startPoint = oGPointer
                        while startPoint not in self.spineTrees[arcNum]:
                            startPoint = pathCopy.pop(0)
                        # we now have an existing startpoint
                        print("       closest existing startpoint is {}".format(startPoint))
                        self.snipSpine(startPoint, destinationPointers, visited)
                if pix in halting:
                    nextPixs.append(pix) # add self back to be explored again
                else:
                    print("    Replacing {} with new neighbors".format(pix))
                    for newNeighbor in newNeighbors:
                        # add to be explored
                        nextPixs.append(newNeighbor)
                        # mark as visited
                        toVisit.add(newNeighbor)
                        # update paths
                        myOGPointer = onPaths[pix]
                        paths[myOGPointer].append(newNeighbor) # add it to the path
                        onPaths[newNeighbor] = myOGPointer # point neighbors to same OG pointer
            # q = list(set(nextPixs))
            # TODO: for testing ----------- #
            seen = set()
            q = [x for x in nextPixs if x not in seen and not seen.add(x)]
            visited.update(toVisit)
        
        for head, path in paths.items():
            print("{}: {}".format(head, path))

        # reset endPoints
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