class ArcHandler:
    def __init__(self):
        self.arcPixels = [] # arcs to pixels
        self.pixelArcs = dict() # pixel to arc
        self.arcBoundaryPixels = [] # arcs to boundary pixels
        self.arcSpinePixels = [] # arcs to spine pixels
        self.completedArcs = [] # arcNum -> boolean

    # make sure we've allocated space for a new arc
    def forceArcInitialized(self, arcNum):
        i = arcNum
        while i >= len(self.arcPixels): # make sure we've initialized arc
            self.arcPixels.append([])
            self.arcBoundaryPixels.append([])
            self.arcSpinePixels.append([])
            self.completedArcs.append(False)

    def addPixelToArc(self, arcNum, pixel, isBoundary=False, isSpine=False):
        if type(pixel) != "tuple":
            print('Error: Pixel must be a tuple')
            return
        self.forceArcInitialized(arcNum) # make sure arc is initialized
        self.arcPixels[arcNum].append(pixel)
        self.pixelArcs[pixel] = arcNum
        if isBoundary:
            self.arcBoundaryPixels[arcNum].append(pixel)
        if isSpine:
            self.arcSpinePixels[arcNum].append(pixel)

    # returns all pixels in an arc
    def getArcPixels(self, arcNum):
        return self.arcPixels[arcNum]

    # returns true if a pixel belongs to an arc
    def pixelHasArc(self, pixel):
        return pixel in self.pixelArcs

    # returns true if an arc has been marked as complete
    def isComplete(self, arcNum):
        if arcNum >= len(self.arcPixels):
            print("Error: Arc doesn't exist yet")
            return
        return self.completedArcs[arcNum]