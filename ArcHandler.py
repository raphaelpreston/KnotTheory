from colour import Color

class ArcHandler:
    def __init__(self):
        self.arcPixels = [] # arcs to pixels (list of sets)
        self.pixelArcs = dict() # pixel to arc
        self.arcBoundaryPixels = [] # arcs to boundary pixels (list of sets)
        self.arcSpinePixels = [] # arcs to spine pixels (list of sets)
        self.pixelSpines = dict() # pixel to spine
        self.spineTrees = [] # for each arc, dict maps pixel => {prev => [], next => []}
        self.spineEndPoints = [] # for each arc, list of endpoints

    # make sure we've allocated space for a new arc
    def forceArcInitialized(self, arcNum):
        i = arcNum
        while i >= len(self.arcPixels): # make sure we've initialized arc
            self.arcPixels.append(set())
            self.arcBoundaryPixels.append(set())
            self.arcSpinePixels.append(set())
            self.spineTrees.append(dict())
            self.spineEndPoints.append(None)

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
        
    # return pixels, colors for a spine map in order to display a color
    # gradient in all distinct lines (to show endpoints)
    def getSpinePaintMap(self, arcNum):
        spinePixels = self.getArcPixels(arcNum, spine=True)
        endPoints = self.getSpineEndPoints(arcNum)
        heads = [p for p in endPoints if self._getSpineNeighbors(p, 'next')]
        joints = [p for p in spinePixels
            if len(self._getSpineNeighbors(p, 'prev') + self._getSpineNeighbors(p, 'next')) > 2]

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
            # for each joint, BFS out from it (all joints at the same time), keeping track of each pixel's distinct line
            # when you reach an end, then you've completed a distinct line
            # if you reach a pixel you've already visited, then combine that pixel's line with yours
            # then you have all your distinct lines
            # next, choose any joint to start at, assign it a color
            # then, for each line that starts at that joint, assign the end of it a different color
            # if that end is another joint, repeat the process. Otherwise done.
            print("Error: This spine has multiple joints. You didn't code that possibilty in, time to do that!")
            return
        
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


if __name__ == "__main__":
    from KnotCanvas import main
    main()