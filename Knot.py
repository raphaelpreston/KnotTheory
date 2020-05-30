from sympy import symbols, Matrix

class Knot:
    def __init__(self, ijkCrossings, ijkCrossingNs, handedness):
        self.ijkCrossings = ijkCrossings
        self.ijkCrossingNs = ijkCrossingNs
        self.handedness = handedness
        self.numUnknots = 0
    
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
    # connected via multiple directions. this won't work if the same arc
    # enters c2 in multiple directions
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


    # return the crossings & (over, under) of each crossing between
    # crossing1 -> crossing2 in the inDir (i0/1, j, or k) direction
    def getCrossingsBetween(self, c1, c2, inDir):

        def getNextDir(incomingDir, currCrossing, nextCrossing):
            if incomingDir == 'i': # not clear if i0 or i1
                if self.ijkCrossingNs[nextCrossing]['i0'] == currCrossing:
                    return 'i1' # cus choosing i0 results in going back
                elif self.ijkCrossingNs[nextCrossing]['i1'] == currCrossing:
                    return 'i0'
                else:
                    print("Error: ")
            else:
                return {'j': 'k', 'k': 'j'}[incomingDir]

        # keep track of crossings inbetween
        crossingsFound = []

        # keep going until we hit our destination crossing
        currCrossing = c1
        currDir = inDir # i0, i1, j, or k
        while True: # want to go at least once

            # get the next crossing in direction
            nextCrossing = self.ijkCrossingNs[currCrossing][currDir]

            # get the incoming direction into the neighbor crossing
            incomingDir = self.getIncomingDir(currCrossing, currDir,
                nextCrossing)
            
            # figure out in which direction to continue searching
            nextDir = getNextDir(incomingDir, currCrossing, nextCrossing)

            # record findings and proceed
            myType = "over" if nextDir in ['i0', 'i1'] else "under"
            crossingsFound.append((nextCrossing, myType))
            currCrossing, currDir = nextCrossing, nextDir

            # break if necessary
            if currCrossing == c2:
                break
        
        # get rid of our destination crossing
        crossingsFound.pop()
        return crossingsFound


    # swap handedness of a given crossing in-place
    def swapCrossing(self, crossingIndex):
        i = self.ijkCrossings[crossingIndex]['i']
        j = self.ijkCrossings[crossingIndex]['j']
        k = self.ijkCrossings[crossingIndex]['k']

        # get the crossings of the i arc, and the other points on j and ks arcs
        iCross0, _ = self.getOrderedICrossings(crossingIndex)
        kCrossOther = self.getOtherJKCrossing(crossingIndex, 'k')


        # get the crossings over which the i, j, or k arcs pass through (as i),
        # but don't need to know the crossings between i and iCross1.
        # the crossings between inherently are crossings where the arc is i
        i0CrossingsAsI = [ # only care about crossing numbers
            c for c, _ in self.getCrossingsBetween(crossingIndex, iCross0, 'i0')
        ]
        kCrossingsAsI = [
            c for c, _ in self.getCrossingsBetween(crossingIndex, kCrossOther, 'k')
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


    # smooth a given crossing in-place, could increase self.numUnknots
    def smoothCrossing(self, c):
        i = self.ijkCrossings[c]['i']
        j = self.ijkCrossings[c]['j']
        k = self.ijkCrossings[c]['k']

        # get the crossings of the i arc, and the other points on j and ks arcs
        iCross0, iCross1 = self.getOrderedICrossings(c)
        jCrossOther = self.getOtherJKCrossing(c, 'j')
        kCrossOther = self.getOtherJKCrossing(c, 'k')

        # k arc becomes i
        # update the crossings on k
        for cBetween, _ in self.getCrossingsBetween(c, kCrossOther, 'k'):
            self.ijkCrossings[cBetween]['i'] = i
        
        # update the other end of k
        self.ijkCrossings[kCrossOther]['j'] = i


        # i1 arc becomes j
        # update the crossings on i1
        for cBetween, _ in self.getCrossingsBetween(c, iCross1, 'i1'):
            self.ijkCrossings[cBetween]['i'] = j

        # update the other end of i1
        self.ijkCrossings[iCross1]['j'] = j


        # update neighbors of all neighbors
        jN = self.ijkCrossingNs[c]['j']
        i1N = self.ijkCrossingNs[c]['i1']
        i0N = self.ijkCrossingNs[c]['i0']
        kN = self.ijkCrossingNs[c]['k']

        # connect neighbors between jN -> i1 curve. need to know if nearest
        # neighbor is the end of the arc to determine direction types
        jNOutDir = 'k' if jCrossOther == jN else 'i1'
        i1NInDir = 'j' if iCross1 == i1N else 'i0'
        self.ijkCrossingNs[jN][jNOutDir] = i1N
        self.ijkCrossingNs[i1N][i1NInDir] = jN

        # connect neighbors between i0 -> k curve
        i0NOutDir = 'k' if iCross0 == i0N else 'i1'
        kNInDir = 'j' if kCrossOther == kN else 'i0'
        self.ijkCrossingNs[i0N][i0NOutDir] = kN
        self.ijkCrossingNs[kN][kNInDir] = i0N

        # determine if we've just made an uknot
        print("Before deleting:")


        # remove crossing from ijkCrossings, and handedness
        self.ijkCrossings[c] = None
        self.ijkCrossingNs[c] = None
        self.handedness[c] = None

    # return an R1 crossing and the crossings between it, or None if none exist
    def getR1Crossing(self):
        # first ensure there aren't trivially R1 crossings with the same arc
        # entering the crossing twice. also, existence will break code below
        for crossing in range(len(self.ijkCrossings)):
            ijk = self.ijkCrossings[crossing]
            if ijk is not None:
                arcs = list(ijk.values())
                # see if any arc appears twice
                doubleArcList = [a for a in arcs if arcs.count(a) > 1]
                if doubleArcList:

                    # get the dirs for the double arc. must be i, j or i, k
                    dirsForArc = [myDir for myDir, _ in ijk.items() if ijk[myDir] == doubleArcList[0]]
                    jOrK = sorted(dirsForArc)[1]

                    # get neighbor in that direction and record it
                    jOrKN = self.ijkCrossingNs[crossing][jOrK]
                    print("Was {}".format(jOrK))

                    # loop goes in i1 direction or i0 direction depending
                    dirToSearch = {"j": "i1", "k": "i0"}[jOrK]

                    print("Found a trivial R1: {} had {}, so searching in {} until {}".format(crossing, doubleArcList, dirToSearch, jOrKN))
                    
                    # shortcut to get crossings between. can't call using crossing
                    # twice because incDir won't work on crossing.
                    between = self.getCrossingsBetween(crossing, jOrKN, dirToSearch)

                    return (crossing, [c for c, _ in between] + [jOrKN])

        # then, all crossings between a given crossing must be "under"
        for crossing in range(len(self.ijkCrossings)):
            ijk = self.ijkCrossings[crossing]
            if ijk is not None:
                for myDir in ['i0', 'i1']: # try both directions
                    print("Crossings between {} are:".format(crossing))
                    between = self.getCrossingsBetween(crossing, crossing, myDir)
                    print(between)
                    if all([myType == "under" for _, myType in between]):
                        print("Found: {}".format((crossing, between)))
                        return (crossing, 
                            [c for c, _ in between]) # only care about crossings
        return None


    # repeatedly reduces all R1 crossings until there are none left
    def reduceR1s(self):
        # a crossing is R1 iff i = j or i = k
        # a crossing is R1 iff i1N = jN = c or i0N = kN = c

        # identify an R1 crossing and remove it via an R1 move
        r1Crossing = self.getR1Crossing()
        print(r1Crossing)

        # if r1Crossing is None:




        # for c in len(self.ijkCrossings):
        #     if self.ijkCrossings[c] is not None:
        #         i0N = self.ijkCrossingNs['i0']
        #         i1N = self.ijkCrossingNs['i1']
        #         jN = self.ijkCrossingNs['j']
        #         kN = self.ijkCrossingNs['k']

        #         if i1N == jN == c: # loops back onto itself

        #             csBetweenSelf = [ # only care about crossings
        #                 c for c, _ in self.getCrossingsBetween(c, c, 'i1')
        #             ]
        #             csBetweenNext = [
        #                 c for c, _ in self.getCrossingsBetween(c, kN, 'k')
        #             ]

        #         elif i0N == kN == c: # R1 crossing in i0 direction
        #             pass
                
        #         for cBetweenSelf in csBetweenSelf:
        #             pass
                    # remove i from crossing <- TODO: make a function for this


    # TODO: working here: skip R1 reductions and move onto HOMFLY
    # TODO: then after we can do R1 and R2 reductions
    

    # TODO: fix everything that will break if it gets a None because that crossings got deleted

    # TODO: can make propogateChange function that will propogate an arc change to the end of an arc

if __name__ == "__main__":


    # figure 8 knot for testing
    ijkCrossings = [
        {'i': 2, 'j': 3, 'k': 0},
        {'i': 3, 'j': 0, 'k': 1},
        {'i': 0, 'j': 1, 'k': 2},
        {'i': 1, 'j': 2, 'k': 3}
    ]
    ijkCrossingNs = [
        {'i0': 2, 'i1': 3, 'j': 1, 'k': 2},
        {'i0': 3, 'i1': 0, 'j': 2, 'k': 3},
        {'i0': 0, 'i1': 1, 'j': 3, 'k': 0},
        {'i0': 1, 'i1': 2, 'j': 0, 'k': 1}
    ]
    handedness = ['left', 'right', 'left', 'right']

    myKnot = Knot(ijkCrossings, ijkCrossingNs, handedness)

    def printStuff():
        print("crossings:")
        for i, c in enumerate(myKnot.ijkCrossings):
            print("  {}: {}".format(i, c))
        print("neighbors: ")
        for i, c in enumerate(myKnot.ijkCrossingNs):
            print("  {}: {}".format(i, c))
        print(handedness)

    print("preswap: ")
    printStuff()

    # test swap crossings
    swap = 0
    myKnot.swapCrossing(swap)

    print("\nAfter swapping {}".format(swap))
    printStuff()

    # test smooth crossings
    # smooth = 1
    # myKnot.smoothCrossing(smooth)

    # print("\nAfter smoothing {}".format(smooth))
    # printStuff()

    # test R1 reduction
    myKnot.reduceR1s()
    print("After reduce R1s:")
    printStuff()

# TODO:
# - undo all trivial R1 moves to cut down on necessary recursive steps also cus ez
# - smooth a crossing
# - write compute function for HOMFLY
# - encorporate KnotDiagram into KnotHandler.py
# - evaluate whether or not to do another invariant, fix spine cleaning, or 
#   start frontend work
# - write algo-style proofs for swapping and smoothing
# - it's possible to undo R2 moves using neighbor checking
# - create an iterator or just a function that returns a path looping around the knot
#  - can be used in getCrossingsBetween and also figuring out if an R1 crossing