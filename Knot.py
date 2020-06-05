from sympy import symbols, Matrix
from random import choice
import copy


class Knot:
    def __init__(self, ijkCrossings, ijkCrossingNs, handedness, numUnknots=0, name=""):
        self.ijkCrossings = ijkCrossings
        self.ijkCrossingNs = ijkCrossingNs
        self.handedness = handedness
        self.numUnknots = numUnknots
        self.name = name
    

    def __str__(self):
        s = "---- Knot {}----\n".format("{} ".format(self.name))
        s += "Crossings:\n"
        for i, c in enumerate(self.ijkCrossings):
            s += "  {}: {}\n".format(i, c)
        s += "Neighbors:\n"
        for i, c in enumerate(self.ijkCrossingNs):
            s += "  {}: {}\n".format(i, c)
        s += "Handedness: {}\n".format(self.handedness)
        s += "Unknots: {}\n".format(self.numUnknots)
        return s

    # return true if myDir is a valid direction
    def checkArcType(self, myDir):
        return myDir in ["i0", "i1", "j", "k"]

    # return true if this knot is an, or series of, unknot(s)
    def isUnlink(self):
        return all([c is None for c in self.ijkCrossings])

    # return the two end-crossings on c's 'i' arc in cyclical order
    def getOrderedICrossings(self, c):
        i = self.ijkCrossings[c]['i']

        # first is the crossing where i = k, second is the crossing where i = j
        first = [ ind for ind, crossings in enumerate(self.ijkCrossings)
                  if crossings and crossings['k'] == i]
        second = [ind for ind, crossings in enumerate(self.ijkCrossings)
                  if crossings and crossings['j'] == i]
        if len(first) > 1 or len(second) > 1:
            print("Error: Found more than one first/second crossing for i")
            print("Firsts: {}".format(first))
            print("Seconds: {}".format(second))
            print("Crossings:")
            for crossing in self.ijkCrossings:
                print(crossing)
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
                         if crossings and crossings[lookingForType] == myArc]
        if len(otherCrossing) > 1:
            print("Error: Found more than one crossing for {}".format(myDir))
            return
        return otherCrossing[0]

    # return the crossings & (over, under) of each crossing between
    # crossing1 -> crossing2 in the inDir (i0/1, j, or k) direction
    # enable forceToTip to force the crossing to keep going until it gets to the
    # end of the arc (incase of a loop around self where you want to go to the end)
    def getCrossingsBetween(self, c1, c2, inDir, forceToTip=False):

        # keep track of crossings inbetween
        crossingsFound = []

        # keep going until we hit our destination crossing
        currCrossing = c1
        currDir = inDir # i0, i1, j, or k
        while True: # want to go at least once

            # get the next crossing in direction and how it arrives to neighbor
            nextCrossing, incDir = self.getNAndDir(currCrossing, currDir)
            
            # figure out in which direction to continue searching
            nextDir = {'i0': 'i1', 'i1': 'i0', 'j': 'k', 'k': 'j'}[incDir]

            # record findings and proceed
            myType = "over" if nextDir in ['i0', 'i1'] else "under"
            crossingsFound.append((nextCrossing, myType))
            currCrossing, currDir = nextCrossing, nextDir

            # break if necessary
            if currCrossing == c2:
                if forceToTip:
                    if myType == "under": # only break when the arc ends
                        break
                else:
                    break
        
        # get rid of our destination crossing
        crossingsFound.pop()
        return crossingsFound
     # return c2's persepective of incoming direction from c1 in outDir to c2
    
    def getNAndDir(self, c1, outDir):
        # get neighbor
        n = self.ijkCrossingNs[c1][outDir]
        # get incoming direction
        return n, self.getIncomingDir(c1, outDir, n)

    # function to return the c1s dir from c2s perspective
    def getIncomingDir(self, c1, outDir, c2):

        # error check
        if self.ijkCrossingNs[c1][outDir] != c2:
            print("Error: C1 -> outdir didn't lead to C2")
            return None
        
        # get the crossings of the i arc, and the other points on j and ks arcs
        iCross0, iCross1 = self.getOrderedICrossings(c1)
        jCrossOther = self.getOtherJKCrossing(c1, 'j')
        kCrossOther = self.getOtherJKCrossing(c1, 'k')

        # get all neighbors
        i0N = self.ijkCrossingNs[c1]['i0']
        i1N = self.ijkCrossingNs[c1]['i1']
        jN = self.ijkCrossingNs[c1]['j']
        kN = self.ijkCrossingNs[c1]['k']

        # intuition is that we can figure out what the incoming direction has to
        # be based on whether or not the other end of the arc is our neighbor

        # special case where c2 is c1's neighbor, incoming on i0/i1, but the i arc
        # loops around back into this crossing, meaning that c2 crossing is
        # technically the end of the arc. we know this is the case if the neighbor
        # of the current crossing in the i1 direction is itself. if the next crossing
        # were anything else, then we would be sure that this wouldn't be the case.
        # TODO: prove this

        # we need to check c1 != c2 to make sure that we don't get stuck in a loop
        if self.ijkCrossingNs[c2]['i1'] == c2 and c1 != c2: # must loop
            modDir = {'i0': 'i', 'i1': 'i', 'j': 'j', 'k': 'k'}[outDir]
            if self.ijkCrossings[c1][modDir] == self.ijkCrossings[c2]['i']:
                # there are at least two crossings, so we know we arrived on i
                # if this is true
                v = {'i1': 'i0', 'k': 'i0', 'i0': 'i1', 'j': 'i1'}[outDir]
            else: # we arrived on j or k
                v = {'i1': 'j', 'k': 'j', 'i0': 'k', 'j': 'k'}[outDir]
        elif self.ijkCrossingNs[c2]['i0'] == c2 and c1 != c2:
            v = 'i1'
        else: # no loop
            v = {
                'i0': 'k' if iCross0 == i0N else 'i1',
                'i1': 'j' if iCross1 == i1N else 'i0',
                'j': 'k' if jCrossOther == jN else 'i1',
                'k': 'j' if kCrossOther == kN else 'i0'
            }[outDir]

        return v

    # swap handedness of a given crossing in-place
    def swapCrossing(self, crossingIndex):
        if crossingIndex is None:
            print("Error: Can't swap a crossing that's already removed")
            return

        i = self.ijkCrossings[crossingIndex]['i']
        j = self.ijkCrossings[crossingIndex]['j']
        k = self.ijkCrossings[crossingIndex]['k']
        myNs = self.ijkCrossingNs[crossingIndex]
        jN, kN, i0N, i1N = myNs['j'], myNs['k'], myNs['i0'], myNs['i1']

        # get the crossings of the i arc, and the other points on j and ks arcs
        iCross0, _ = self.getOrderedICrossings(crossingIndex)
        kCrossOther = self.getOtherJKCrossing(crossingIndex, 'k')


        # get the crossings over which the i, j, or k arcs pass through (as i),
        # but don't need to know the crossings between i and iCross1.
        # the crossings between inherently are crossings where the arc is i
        i0CrossingsAsI = [ # only care about crossing numbers
            c for c, _ in self.getCrossingsBetween(crossingIndex, iCross0, 'i0', forceToTip=True)
        ]
        kCrossingsAsI = [
            c for c, _ in self.getCrossingsBetween(crossingIndex, kCrossOther, 'k', forceToTip=True)
        ]
        
        # special cases where we are swapping a loop
        if i1N == crossingIndex:
            newK, newI = k, k
            newJ = i
        elif i0N == crossingIndex:
            newJ, newI = j, j
            newK = i
        else: # not a loop
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

        # update the neighbors
        myNs['i0'], myNs['i1'], myNs['j'], myNs['k'] = jN, kN, i0N, i1N

        # replace our crossing with the new values
        self.ijkCrossings[crossingIndex] = {'i': newI, 'j': newJ, 'k': newK}

        # switch the handedness
        self.handedness[crossingIndex] = "left" if self.handedness == "right" else "right"

    # smooth a given crossing in-place, could increase self.numUnknots
    def smoothCrossing(self, c):
        if c is None:
            print("Error: Can't smooth a crossing that's already removed")
            return
        
        # get all info needed
        i = self.ijkCrossings[c]['i']
        j = self.ijkCrossings[c]['j']
        k = self.ijkCrossings[c]['k']
        i0N, i0NIncDir = self.getNAndDir(c, 'i0')
        i1N, i1NIncDir = self.getNAndDir(c, 'i1')
        jN, jNIncDir = self.getNAndDir(c, 'j')
        kN, kNIncDir = self.getNAndDir(c, 'k')

        # get the crossings of the i arc, and the other points on j and ks arcs
        iCross0, iCross1 = self.getOrderedICrossings(c)
        jCrossOther = self.getOtherJKCrossing(c, 'j')
        kCrossOther = self.getOtherJKCrossing(c, 'k')

        # get relevent crossings inbetween crossings
        kCrossingsAsI = self.getCrossingsBetween(c, kCrossOther, 'k', forceToTip=True)
        i1CrossingsAsI = self.getCrossingsBetween(c, iCross1, 'i1', forceToTip=True)

        # check for number of unknots to be made
        if i0N == c and i1N == c:
            numUnknotsMade = 2
        elif i0N == c or i1N == c:
            numUnknotsMade = 1
        else:
            numUnknotsMade = 0

        # k arc becomes i
        # update the crossings on k
        for cBetween, _ in kCrossingsAsI:
            self.ijkCrossings[cBetween]['i'] = i
        
        # update the other end of k
        self.ijkCrossings[kCrossOther]['j'] = i

        # i1 arc becomes j
        # update the crossings on i1
        for cBetween, _ in i1CrossingsAsI:
            self.ijkCrossings[cBetween]['i'] = j

        # update the other end of i1
        self.ijkCrossings[iCross1]['j'] = j

        # connect neighbors between jN -> i1 curve
        self.ijkCrossingNs[jN][jNIncDir] = i1N
        self.ijkCrossingNs[i1N][i1NIncDir] = jN

        # connect neighbors between i0 -> k curve
        self.ijkCrossingNs[i0N][i0NIncDir] = kN
        self.ijkCrossingNs[kN][kNIncDir] = i0N

        # remove crossing from ijkCrossings, and handedness
        self.ijkCrossings[c] = None
        self.ijkCrossingNs[c] = None
        self.handedness[c] = None

        # special case where we've removed all crossings except one
        if len([c for c in self.ijkCrossings if c is not None]) == 1:
            ind = [i for i, c in enumerate(self.ijkCrossings) if c is not None][0]
            # set all i, j, k to be itself
            self.ijkCrossings[ind] = {'i': ind, 'j': ind, 'k': ind}

        # incease the number of unknots
        self.numUnknots += numUnknotsMade

    # return an R1 crossing and the crossings between it, or None if none exist.
    # guaranteed to not return a crossing in a direction with a path with a vertex
    # that appears twice
    def getR1Crossing(self):
        # first ensure there aren't trivially R1 crossings with the same arc
        # entering the crossing twice. also, existence will break code further down
        for crossing in range(len(self.ijkCrossings)):
            ijk = self.ijkCrossings[crossing]
            if ijk is not None:
                arcs = list(ijk.values())
                # see if any arc appears twice in a crossing
                doubleArcList = [a for a in arcs if arcs.count(a) > 1]
                if doubleArcList:

                    # get the dirs for the double arc. must be i, j or i, k
                    dirsForArc = [myDir for myDir, _ in ijk.items() if ijk[myDir] == doubleArcList[0]]
                    jOrK = sorted(dirsForArc)[1]

                    # get neighbor in that direction and record it
                    jOrKN = self.ijkCrossingNs[crossing][jOrK]

                    # loop goes in i1 direction or i0 direction depending
                    dirToSearch = {"j": "i1", "k": "i0"}[jOrK]

                    # skip looking if it's a trivial loop
                    if jOrKN == crossing:
                        return (crossing, [], dirToSearch, "over")

                    # shortcut to get crossings between. can't call using crossing
                    # twice because incDir won't work on crossing. < dunno bout this anymore
                    between = self.getCrossingsBetween(crossing, jOrKN, dirToSearch)
                    csBetween = [c for c, _ in between] + [jOrKN]
                    
                    # special case to detect a link - can't reduce a link
                    if len(csBetween) != 1:
                        return (crossing, csBetween, dirToSearch, "over")

        # then, all crossings between a given crossing need to be "under"
        for crossing in range(len(self.ijkCrossings)):
            ijk = self.ijkCrossings[crossing]
            if ijk is not None:
                for myDir in ['i0', 'i1']: # try both directions
                    between = self.getCrossingsBetween(crossing, crossing, myDir)
                    if all([myType == "under" for _, myType in between]):
                        # special case to detect a link - can't reduce a link
                        if len(csBetween) != 1:
                            return (
                                crossing, 
                                [c for c, _ in between], # only care about crossings
                                myDir,
                                "under"
                            )
        return None, None, None, None

    # repeatedly reduces all R1 crossings until there are none left
    def reduceR1s(self, numReductions=float("inf")):

        # TODO: this will break if a crossing being removed changes another
        # TODO: crossing that was on the path to be removed. prove it won't

        # identify an R1 crossing and remove it via an R1 move
        # we know that the path doesn't contain the same vertex twice
        reduced = 0
        while True:
            print("Reduction #{}".format(reduced))
            c, csBetweenSelf, myDir, pathType = self.getR1Crossing()
            if c is not None and reduced < numReductions:
                for cBetweenSelf in csBetweenSelf + [c]: # must remove c last
                    print("  - Remove {}".format(cBetweenSelf))
                    self.removeCrossing(cBetweenSelf)
                reduced += 1
            else:
                print(" - nothing, all done")
                break

    # remove a crossing from a knot diagram, connecting the neighbors to each other
    # it's possible that this puts the diagram in an invalid state
    def removeCrossing(self, c):
        # get the arcs
        crossing = self.ijkCrossings[c]
        if crossing is None:
            print("Error: Can't remove a crossing that's already removed")
            return
        i, j, k = crossing['i'], crossing['j'], crossing['k']

        # get neighbors and their incoming directions from c into given neighbor
        i0N, i0NInc = self.getNAndDir(c, 'i0')
        i1N, i1NInc = self.getNAndDir(c, 'i1')
        jN, jNInc = self.getNAndDir(c, 'j')
        kN, kNInc = self.getNAndDir(c, 'k')
        
        # save ijkCrossing changes locally so getCrossingsBetween works
        ijkCrossings = copy.deepcopy(self.ijkCrossings)
        ijkCrossingNs = copy.deepcopy(self.ijkCrossingNs)

        # this crossing could be the only one left on its knot
        if all([n == jN for n in [i1N, i0N, kN]]):
            # no arcs or neighbors to set, just increase unknots
            self.numUnknots += 1
        else:
            # update arcs
            jCrossOther = self.getOtherJKCrossing(c, 'j')
            kCrossOther = self.getOtherJKCrossing(c, 'k')

            # the k arc becomes the j arc
            for cr, _ in self.getCrossingsBetween(c, kCrossOther, 'k', forceToTip=True):
                ijkCrossings[cr]['i'] = j

            # update the tip of the k arc
            ijkCrossings[kCrossOther]['j'] = j

            # at any step, if we are setting a neighbor's neighbor to be c (which
            # we are removing), there must be a loop around c in some direction
            # and we need to instead set it to be the NEXT neighbor after the loop

            # update neighbors and get the next neighbors after the loop if necessary
            
            if i1N == c:
                ijkCrossingNs[kN][kNInc] = self.ijkCrossingNs[c]['i0']
                ijkCrossingNs[i0N][i0NInc] = self.ijkCrossingNs[c]['k']
            elif i0N == c:
                ijkCrossingNs[jN][jNInc] = self.ijkCrossingNs[c]['i1']
                ijkCrossingNs[i1N][i1NInc] = self.ijkCrossingNs[c]['j']
            else: # no loop
                ijkCrossingNs[jN][jNInc] = kN
                ijkCrossingNs[kN][kNInc] = jN
                ijkCrossingNs[i0N][i0NInc] = i1N
                ijkCrossingNs[i1N][i1NInc] = i0N
        
        # commit local crossing and neighbor changes
        self.ijkCrossings = ijkCrossings
        self.ijkCrossingNs = ijkCrossingNs

        # remove crossing
        self.ijkCrossings[c] = None
        self.ijkCrossingNs[c] = None
        self.handedness[c] = None

    # return a duplicated version of this knot (optionally named)
    def duplicate(self, name=""):
        return Knot(self.ijkCrossings, self.ijkCrossingNs, self.handedness, self.numUnknots, name)


    # internal recursive function for computing homfly
    def _homfly(self, k, l, m, distCrossing=None):
        print("{}: computing HOMFLY:".format(k.name))
        print(k)

        # reduce all R1 crossings out of our knot
        k.reduceR1s()
        k.name += "r"
        print(k)

        # base case: k is an unlink of n components
        if k.isUnlink():
            n = k.numUnknots
            poly = (-m**-1)**(n-1) * (l + l**(-1))**(n-1)
            print("{}: hit basecase, n={}:  {}".format(k.name, n, poly))
            return poly

        # get our distinguished crossing if not given
        if distCrossing is None:
            validCrossings = [i for i, c in enumerate(k.ijkCrossings) if c is not None]
            distCrossing = validCrossings[0]
        isRight = {'right': True, 'left': False}[k.handedness[distCrossing]]
        # print("{}: distinguished crossing {} ({} handed)".format(k.name, distCrossing, "right" if isRight else "left"))
            
        # copy knot and modify accordingly
        kR, kL, kS = k.duplicate(), k.duplicate(), k.duplicate()
        if isRight:
            print("{}: swapping '{}' from right to left".format(k.name, distCrossing))
            kL.swapCrossing(distCrossing)
        else:
            print("{}: swapping '{}' from left to right".format(k.name, distCrossing))
            kR.swapCrossing(distCrossing)
        print("{}: smoothing '{}'".format(k.name, distCrossing))
        kS.smoothCrossing(distCrossing)

        # assign new names
        kR.name += "r"
        kL.name += "l"
        kS.name += "s"

        print("Right Handed: ")
        print(kR)
        print("Left Handed: ")
        print(kL)
        print("Smoothed: ")
        print(kS)

        # compute necessary polynomials
        # if isRight:
        #     pL = self._homfly(kL, l, m)
        #     print("{}: solved: {}".format(kL.name, pL))
        # else:
        #     pR = self._homfly(kR, l, m)
        #     print("{}: solved: {}".format(kR.name, pR))
        # pS = self._homfly(kS, l, m)
        # print("{}: solved: {}".format(kS.name, pS))

        # # return equation solved for the correct polynomial
        # if isRight:
        #     v = (-m * pS - l**-1 * pL) * l**-1
        # else:
        #     v = (-m * pS - l * pR) * l
        # print("{}: returning {}".format(k.name, v))
        # return v

    # recursively compute the homfly polynomial
    def computeHomfly(self):

        # share symbols with all new knots' equations
        l, m = symbols("l m")

        return self._homfly(self.duplicate(name="K"), l, m)


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

 
    # print(myKnot.computeHomfly())

    ################## -------------- TS5 --------- ##############

    print("original: ")
    print(myKnot)

    # smooth 0
    smooth = 0
    myKnot.smoothCrossing(smooth)
    print("\nAfter smoothing {}".format(smooth))
    print(myKnot)

    # reduce
    myKnot.reduceR1s()
    print("\nAfter reducing")
    print(myKnot)

    # swap 1
    swap = 1
    myKnot.swapCrossing(swap)
    print("\nAfter swapping {}".format(swap))
    print(myKnot)

    # # reduce
    # myKnot.reduceR1s()
    # print("\nAfter reducing")
    # print(myKnot)


    ################## -------------- NEW2 ------------ ###############
    # print("original: ")
    # printStuff()

    # # test swap crossings
    # swap = 0
    # myKnot.swapCrossing(swap)
    # print("\nAfter swapping {}".format(swap))
    # printStuff()

    # # test reduce
    # myKnot.reduceR1s()
    # print("\nAfter reducing")
    # printStuff()

    ################ ------------- NEW1 ------------- ###############
    # print("original: ")
    # printStuff()

    # print("\nGetting an R1 should be None: {}".format(myKnot.getR1Crossing()))

    # # test swap crossings
    # swap = 0
    # myKnot.swapCrossing(swap)
    # print("\nAfter swapping {}".format(swap))
    # printStuff()

    # print("\nGetting an R1 should be (1, [0, 2], 'i1', 'over'): {}".format(myKnot.getR1Crossing()))

    # # test removal
    # remove = 0
    # myKnot.removeCrossing(remove)
    # print("\nAfter removing {}".format(remove))
    # printStuff()

    # # test removal
    # remove = 2
    # myKnot.removeCrossing(remove)
    # print("\nAfter removing {}".format(remove))
    # printStuff()

    # print("\nGetting an R1 should be (1, [], 'over'): {}".format(myKnot.getR1Crossing()))

    # # test removal
    # remove = 1
    # myKnot.removeCrossing(remove)
    # print("\nAfter removing {}".format(remove))
    # printStuff()

    # print("\nGetting an R1 should be (3, [], 'over'): {}".format(myKnot.getR1Crossing()))

    # # test removal
    # remove = 3
    # myKnot.removeCrossing(remove)
    # print("\nAfter removing {}".format(remove))
    # printStuff()

    # print("\nGetting an R1 should be None: {}".format(myKnot.getR1Crossing()))


#################### ------------------------------ #################





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
# in theory, we technically don't need to know how each neighbor arrives:
        # jNOutDir = 'k' if jCrossOther == jN else 'i1'
        # i1NInDir = 'j' if iCross1 == i1N else 'i0'
        # i0NOutDir = 'k' if iCross0 == i0N else 'i1'
        # kNInDir = 'j' if kCrossOther == kN else 'i0'