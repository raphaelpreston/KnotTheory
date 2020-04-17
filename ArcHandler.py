class ArcHandler:
    def __init__(self):
        self.arcPixels = [] # arcs to pixels (list of sets)
        self.pixelArcs = dict() # pixel to arc
        self.arcBoundaryPixels = [] # arcs to boundary pixels (list of sets)
        self.arcSpinePixels = [] # arcs to spine pixels (list of sets)
        self.pixelSpines = dict() # pixel to spine
        self.completedArcs = [] # arcNum -> boolean

    # make sure we've allocated space for a new arc
    def forceArcInitialized(self, arcNum):
        i = arcNum
        while i >= len(self.arcPixels): # make sure we've initialized arc
            self.arcPixels.append(set())
            self.arcBoundaryPixels.append(set())
            self.arcSpinePixels.append(set())
            self.completedArcs.append(False)

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
            self.arcBoundaryPixels[arcNum].add(pixel)
        if isSpine:
            self.arcSpinePixels[arcNum].add(pixel)
            if pixel in self.pixelSpines and self.pixelSpines[pixel] != arcNum:
                print('Warning: Reassigning pixel {} from spine {} to spine {}'.format(pixel, self.pixelSpines[pixel], arcNum))
            self.pixelSpines[pixel] = arcNum

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
    
    # returns true if a pixel belongs to a spine
    def pixelHasSpine(self, pixel):
        return pixel in self.pixelSpines

    # returns true if an arc has been marked as complete
    def isComplete(self, arcNum):
        if arcNum >= len(self.arcPixels):
            print("Error: Arc doesn't exist yet")
            return
        return self.completedArcs[arcNum]
    
    # set an arc as completed
    def setCompleted(self, arcNum):
        self.completedArcs[arcNum] = True
    
    def numCompletedArcs(self):
        return self.completedArcs.count(True)

if __name__ == "__main__":
    from KnotCanvas import main
    main()