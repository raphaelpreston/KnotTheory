from sympy import symbols, Matrix

class Knot:
    def __init__(self, ijkCrossings, ijkCrossingNs, handedness):
        self.ijkCrossings = ijkCrossings
        self.ijkCrossingNs = ijkCrossingNs
        self.handedness = handedness
    
    # return true if myDir is a valid direction
    def checkArcType(self, myDir):
        return myDir in ["i0", "i1", "j", "k"]

    # return true if this knot is the unknot
    def isUnknot(self):
        return len(self.ijkCrossings) == 0


    # return the type (i, j, k) (not i0/i1), of an arc given a crossing in which
    # it's a part of
    def getDirFromArcNum(self, c, arcNum):
        myCrossing = self.ijkCrossings[c]
        for arcType, otherArcNum in myCrossing.items():
            if arcNum == otherArcNum:
                return arcType
        return None


    # return the two end-crossings on c's 'i' arc in cyclical order
    def getOrderedICrossings(self, c):
        i = self.ijkCrossings[c]['i']

        # first is the crossing where i = k, second is the crossing where i = j
        first = [ ind for ind, crossings in enumerate(self.ijkCrossings)
                  if crossings['k'] == i]
        second = [ind for ind, crossings in enumerate(self.ijkCrossings)
                  if crossings['j'] == i]
        if len(first) > 1 or len(second) > 1:
            print("Error: Found more than one first/second crossing for i")
            return
        return first[0], second[0]


    # return the crossing at the other end of c's arc in the 'i' or 'j' dir
    def getOtherJKCrossing(self, c, myDir):
        if myDir != "j" and myDir != "k":
            print("Error: Only used for j and k, not {}".format(myDir))
            return
        myArc = self.ijkCrossings[c][myDir]
        lookingForType = "k" if myDir == "j" else "j"
        otherCrossing = [ind for ind, crossings in enumerate(self.ijkCrossings)
                         if crossings[lookingForType] == myArc]
        if len(otherCrossing) > 1:
            print("Error: Found more than one crossing for {}".format(myDir))
            return
        return otherCrossing[0]
    

    # returns the incoming direction from c1 into c2 given outgoing dir from c1
    # you need an outgoing dir because it's possible that crossings are
    # connected via multiple directions
    def getIncomingDir(self, c1, outDir, c2):
        # error check
        if self.ijkCrossingNs[c1][outDir] != c2:
            print("Error: C1 -> outdir didn't lead to C2")
            return
        
        # simplify direction to i if it's i0/i1
        modifiedDir = "i" if outDir == "i0" or outDir == "i1" else outDir

        # get the arcNum on which we departed from c1 and arrived onto c2
        arrivalArc = self.ijkCrossings[c1][modifiedDir]

        # the incoming direction is the dir which is the incoming arc
        return self.getDirFromArcNum(c2, arrivalArc)


    # return the crossings between crossing1 -> crossing2 in the inDir (i0/1,
    # j, or k) direction
    def getCrossingsBetween(self, c1, c2, inDir):
        # keep track of crossings inbetween
        crossingsFound = []

        # keep going until we hit our destination crossing
        currCrossing = c1
        currDir = inDir # i0, i1, j, or k
        while currCrossing != c2:

            # get the next crossing in direction
            nextCrossing = self.ijkCrossingNs[currCrossing][currDir]

            # get the incoming direction into the neighbor crossing
            incomingDir = self.getIncomingDir(currCrossing, currDir,
                nextCrossing)
            
            # figure out in which direction to continue searching
            if incomingDir == 'i': # not clear if i0 or i1
                if self.ijkCrossingNs[nextCrossing]['i0'] == currCrossing:
                    nextDir = 'i1' # cus choosing i0 results in going back
                elif self.ijkCrossingNs[nextCrossing]['i1'] == currCrossing:
                    nextDir = 'i0'
            else:
                nextDir = {'j': 'k', 'k': 'j'}[incomingDir]
            
            # record findings and proceed
            crossingsFound.append(nextCrossing)
            currCrossing, currDir = nextCrossing, nextDir
        
        # get rid of our destination crossing
        crossingsFound.pop()
        return crossingsFound


    # swap handedness of a given crossing in-place
    def swapCrossing(self, crossingIndex):
        i = self.ijkCrossings[crossingIndex]['i']
        j = self.ijkCrossings[crossingIndex]['j']
        k = self.ijkCrossings[crossingIndex]['k']

        # get the endpoints of the i arc, and the other points on j and ks arcs
        iCross0, _ = self.getOrderedICrossings(crossingIndex)
        kCrossOther = self.getOtherJKCrossing(crossingIndex, 'k')


        # get the crossings over which the i, j, or k arcs pass through (as i),
        # but don't need to know the crossings between i and iCross1.
        # the crossings between inherently are crossings where the arc is i
        i0CrossingsAsI = [
            c for c in self.getCrossingsBetween(crossingIndex, iCross0, 'i0')
        ]
        kCrossingsAsI =  [
            c for c in self.getCrossingsBetween(crossingIndex, kCrossOther, 'k')
        ]

        
        # from crossing -> iCross1 stays i's old arcNum, but it's the new k
        newK = i
        # all crossings between crossing -> iCross1 stay constant

        # the new arc formed from iCross0 to crossing steals k's arcNum since
        # k's arcNum will be engulfed by j
        newJ = k

        # update all crossings inbetween crossing and iCross0
        for c in i0CrossingsAsI:
            self.ijkCrossings[c]['i'] = k
        
        # change the value at iCross0 too
        self.ijkCrossings[iCross0]['k'] = k

        # j's arcNum extends into k to become the new i
        newI = j

        # update crossings between crossing and other tip of k
        for c in kCrossingsAsI:
            self.ijkCrossings[c]['i'] = j

        # update the value at tip of k
        self.ijkCrossings[kCrossOther]['j'] = j

        # the i's on crossings between crossing and other tip of j stay constant
        # as well as the tip of j

        # swap the neighbors
        myNs = self.ijkCrossingNs[crossingIndex]
        myNs['i0'], myNs['i1'], myNs['j'], myNs['k'] = (
            myNs['j'], myNs['k'], myNs['i0'], myNs['i1']
        )

        # replace our crossing with the new values
        self.ijkCrossings[crossingIndex] = {'i': newI, 'j': newJ, 'k': newK}

        # # switch the handedness
        self.handedness[crossingIndex] = "left" if self.handedness == "right" else "right"


    # smooth a given crossing in-place
    def smoothCrossing(self, c):
        pass

if __name__ == "__main__":
    import HomflyPolyTools

# TODO:
# - undo all trivial R1 moves to cut down on necessary recursive steps also cus ez
# - smooth a crossing
# - write compute function for HOMFLY
# - encorporate KnotDiagram into KnotHandler.py
# - evaluate whether or not to do another invariant, fix spine cleaning, or 
#   start frontend work
# - write algo-style proofs for swapping and smoothing
# - it's possible to undo R2 moves using neighbor checking