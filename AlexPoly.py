import ImageTools as it
from sympy import symbols, Matrix, init_printing

# (traveled, not absolute), length of line created by the pixels on i to test
# handedness of crossing
I_LINE_LEN = 10

# printing method adapted from
# https://stackoverflow.com/questions/13214809/pretty-print-2d-python-list
def pm(A):
    if type(A) is Matrix:
        A = A.tolist()
    print('\n'.join(['\t'.join([str(cell) for cell in row]) for row in A]))


class AlexPoly:
    # takes an arcHandler
    def __init__(self, ah):
        self.ah = ah
        self.matrix = None # nxn 2d matrix
        self.ijkCrossings = None # crossingNumber => {"i": {arcNum}, "j"..., "k"...}
        self.handedness = None # crossingNumber => "RH" or "LH"
        self.poly = None

        # todo: maybe smart to get the endpoints for all i,j,k and store them for future use?


    def getIJKCrossingsAndHandedness(self):
        # crossings are stored as arcNum => {endPoint => endPoint (of other arc)}
        ijkTuples = [] # tuples of (i,j,k)
        self.handedness = [] # "left" or "right"
        crossingsSeen = set()
        # for each arcNum
        for myArcNum, data in enumerate(self.ah.crossings):
            # for each arc it connects to
            for myEp, otherEp in data.items():

                # skip if we've seen it before
                if (myEp, otherEp) in crossingsSeen or \
                        (otherEp, myEp) in crossingsSeen:
                    continue

                crossingsSeen.add((myEp, otherEp))
                otherArcNum = self.ah.getPixelArc(otherEp)

                # figure out which arc is between the endpoints
                # use rectangle because lines might cross without intersecting
                # diagonally
                pixelsBetween = it.getRectangle(myEp, otherEp, 2)
                spinesBetween = set()
                pixsOnI = set() # keep track of pixels on i's spine btwn j & k
                for pix in pixelsBetween:
                    if self.ah.pixelHasSpine(pix):
                        spineNum = self.ah.getPixelSpine(pix)
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
                myEpNext = self.ah.knotEnumeration[myEp]["next"]
                myEpPrev = self.ah.knotEnumeration[myEp]["prev"]
                i = spinesBetween[0]
                if otherEp == myEpNext: # goes from myEp to otherEp
                    j, k = myArcNum, otherArcNum
                    jEp, kEp = myEp, otherEp
                elif otherEp == myEpPrev: # goes from otherEp to myEp
                    k, j = myArcNum, otherArcNum
                    kEp, jEp = myEp, otherEp
                else:
                    print("Error: Supposed EP connection wasn't in any neighbors")
                    return
                
                # record the i,j,k values
                ijkTuples.append((i, j, k)) 
                
                # figure out handedness
                # form imaginary line on i around the pixels on i between j & k
                iPoint = pixsOnI.pop() # arbitrary

                # traverse both ways down i to form imaginary line
                nextN = self.ah.knotEnumeration[iPoint]["next"]
                prevN = self.ah.knotEnumeration[iPoint]["prev"]
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
                        nextN = self.ah.knotEnumeration[currPix][myDir]
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
                pixelOnSide = it.pixelOnSide(p1, p2, jEp)
                if pixelOnSide == None:
                    print("Error: pixel {} is on the line".format(jEp))
                    return
                # appending to self.handedness does preserve order
                self.handedness.append(pixelOnSide)
        # convert into ijkCrossings
        self.ijkCrossings = []
        for i, j, k in ijkTuples:
            self.ijkCrossings.append({"i": i, "j": j, "k": k})

    def getHandedness(self):
        def getJKPoints(j, k):
            jCrossings = self.ah.crossings[j]
            kCrossings = self.ah.crossings[k]
            jEps = []
            for ep, potK in jCrossings.items(): # for all the endpoints on j
                if self.ah.getPixelSpine(potK) == k: # if it connects to k
                    jEps.append(ep)
            kEps = []
            for ep, potJ in kCrossings.items():
                if self.ah.getPixelSpine(potJ) == j:
                    kEps.append(ep)
            if len(jEps) > 1 or len(kEps) > 1:
                print("Error: Found multiple points that match crossing")
                return
            if len(jEps) < 1 or len(kEps) < 1:
                print("Error: Found no points that match crossing")
                return
            return jEps[0], kEps[0]
        
        # for each crossing
        self.handedness = [None for _ in self.ijkCrossings]
        for crossingNum, ijkCrossingData in enumerate(self.ijkCrossings):
            # determine on which side of the line created by "i" lies the "j" ep
            i = ijkCrossingData["i"]
            j = ijkCrossingData["j"]
            k = ijkCrossingData["k"]

            # get j and k endpoints
            jEp, kEp = getJKPoints(j, k)

            # print("Checking crossing {}: {}".format(crossingNum, ijkCrossingData))
            # print(" jEP: {}".format(jEp))
            # print(" kEP: {}".format(kEp))

            # get points on i to form imaginary line
            # figure out which pixels are between the endpoints # TODO: THIS IS A kinda COPY PASTE FROM ABOVE
            pixelsBetween = it.getRectangle(jEp, kEp, 2)
            pixsOnI = set() # if we got here, we know there's only one arc between eps
            for pix in pixelsBetween:
                if self.ah.pixelHasSpine(pix):
                    spineNum = self.ah.getPixelSpine(pix)
                    if spineNum != j and spineNum != k:
                        if spineNum != i:
                            print("Error: Spine inbetween wasn't i!")
                            return
                        pixsOnI.add(pix)
            iPoint = pixsOnI.pop() # choose an aribitrary i (choosing the midpoint would be better in theory)
            
            # traverse both ways down i to form imaginary line
            nextN = self.ah.knotEnumeration[iPoint]["next"]
            prevN = self.ah.knotEnumeration[iPoint]["prev"]
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
                    nextN = self.ah.knotEnumeration[currPix][myDir]
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
            
            # print("pos: {}\nneg: {}".format(posLine, negLine))
            # last of the neg -> last of the pos
            p1 = negLine[-1]
            p2 = posLine[-1]

            # print("Calling sideOfPixel({}, {}, {})".format(p1, p2, jEp))
            pixelOnSide = it.pixelOnSide(p1, p2, jEp)
            if pixelOnSide == None:
                print("Error: pixel {} is on the line".format(jEp))
                return
            # print("got {}".format(sideOfPixel))
            self.handedness[crossingNum] = pixelOnSide

    def getMatrix(self):
        # initialize matrix
        n = len(self.ijkCrossings) # same as number of arcs
        A = [[0 for _ in range(n)] for _ in range(n)]
        t = symbols('t')
        # each row corresponds to a crossing
        for crossingNum in range(n):
            row = A[crossingNum]
            i = self.ijkCrossings[crossingNum]["i"]
            j = self.ijkCrossings[crossingNum]["j"]
            k = self.ijkCrossings[crossingNum]["k"]

            # 1-t in the ith col
            row[i] = 1-t
            if self.handedness[crossingNum] == "right":
                row[j] = -1 # -1 in jth col
                row[k] = t # t in kth col
            elif self.handedness[crossingNum] == "left":
                row[j] = t # t in jth col
                row[k] = -1 # -1 in kth col
            else:
                print("Error: Unrecognized handedness.")
                return
        print("Raw Matrix:")
        pm(A)

        # remove last row and column to get Alexander Matrix
        aMat = Matrix(A)
        # aMat = [[A[row][col] for col in range(n)] for row in range(n)]
        aMat.col_del(n-1)
        aMat.row_del(n-1)
        
        self.matrix = aMat

    def getPoly(self):
        self.poly = self.matrix.det()


    def compute(self):
        # get the i,j,k values and RH/LH data for all crossings
        self.getIJKCrossingsAndHandedness()
        print("IJK Crossings:")
        print(self.ijkCrossings)
        # self.getHandedness()
        print("Handedness")
        print(self.handedness)
        self.getMatrix()
        print("Alexander Matrix:")
        pm(self.matrix)
        print(self.matrix.tolist())
        self.getPoly()
        print("Polynomial:")
        print(self.poly)


if __name__ == "__main__":
    from KnotCanvas import main
    main()

