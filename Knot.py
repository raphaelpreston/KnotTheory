from sympy import symbols, Matrix
from random import choice
import copy


class Knot:
    def __init__(self, ijkCrossings, handedness, numUnknots=0, name=""):
        self.ijkCrossings = ijkCrossings
        self.handedness = handedness
        self.numUnknots = numUnknots
        self.name = name
    

    def __str__(self):
        s = "---- Knot {}----\n".format("{} ".format(self.name))
        s += "Crossings:\n"
        for i, c in enumerate(self.ijkCrossings):
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
    
    # return the neighbor in a direction from c, and the incoming direction on said neighbor
    def getNAndDir(self, c, myDir):
        # get arcNum in that direction
        myArc = self.ijkCrossings[c][myDir]

        # get all crossings that share the arc
        crossingsOnArc = [
            cr for cr, cData in enumerate(self.ijkCrossings) if 
            any([arc == myArc for _, arc in cData.items()])
        ]

        # guaranteed to have two crossings per arc
        n = [cr for cr in crossingsOnArc if cr != c][0]

        # get the incoming direction on that crossing
        incDir = [myDir for myDir, arc in self.ijkCrossings[n].items() if arc == myArc][0]

        return n, incDir

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

    # update a crossing with given dirs and crossings in newCrossings
    # propogate the change the neighbors as well
    def updateCrossing(self, c, newCrossings):
        for myDir, newArc in newCrossings.items():
            # get info first
            n, nIncDir = self.getNAndDir(c, myDir)

            # update self
            self.ijkCrossings[c][myDir] = newArc

            # update neighbor
            self.ijkCrossings[n][nIncDir] = newArc

    # swap handedness of a given crossing in-place
    def swapCrossing(self, c):
        if c is None:
            print("Error: Can't swap a crossing that's already removed")
            return

        # get all affected neighbors
        # i0N, i0NInc = self.getNAndDir(c, 'i0')
        # i1N, i1NInc = self.getNAndDir(c, 'i1')
        # jN, jNInc = self.getNAndDir(c, 'j')
        # kN, kNInc = self.getNAndDir(c, 'k')

        # # update own crossing
        # newI0, newI1, newJ, newK = j, k, i0, i1

        # # update all neighboring crossings
        # self.ijkCrossings[i0N][i0nInc] = 

        # get connected arcs
        i0 = self.ijkCrossings[c]['i0']
        i1 = self.ijkCrossings[c]['i1']
        j = self.ijkCrossings[c]['j']
        k = self.ijkCrossings[c]['k']

        # swap crossing and propogate changes
        self.updateCrossing(c, {
            'i0': j,
            'i1': k,
            'j': i0,
            'k': i1
        })

        # switch the handedness
        self.handedness = {'left': 'right', 'right': 'left'}[self.handedness[c]]

    # smooth a given crossing in-place, could increase self.numUnknots
    def smoothCrossing(self, c):
        if c is None:
            print("Error: Can't smooth a crossing that's already removed")
            return

        # get all info needed
        i0 = self.ijkCrossings[c]['i0']
        i1 = self.ijkCrossings[c]['i1']
        j = self.ijkCrossings[c]['j']
        k = self.ijkCrossings[c]['k']

        # check for the number of arcs that are the same
        numSameArcs = 4 - len(set([i0, i1, j, k]))

        # let j and i0 take over k and i1 to propogate change to neighbors
        self.updateCrossing(c, {
            'i1': j,
            'k': i0,
        })

        print("After updating:")
        print(self)

        # remove crossing
        self.ijkCrossings[c] = None
        self.handedness[c] = None

        # increase the number of unknots
        self.numUnknots += numSameArcs


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
        {'i0': 3, 'i1': 4, 'j': 6, 'k': 7},
        {'i0': 5, 'i1': 6, 'j': 0, 'k': 1},
        {'i0': 7, 'i1': 0, 'j': 2, 'k': 3},
        {'i0': 1, 'i1': 2, 'j': 4, 'k': 5},
    ]
    # ijkCrossingNs = [
    #     {'i0': 2, 'i1': 3, 'j': 1, 'k': 2},
    #     {'i0': 3, 'i1': 0, 'j': 2, 'k': 3},
    #     {'i0': 0, 'i1': 1, 'j': 3, 'k': 0},
    #     {'i0': 1, 'i1': 2, 'j': 0, 'k': 1}
    # ]
    handedness = ['left', 'right', 'left', 'right']

    myKnot = Knot(ijkCrossings, handedness)

    print("original: ")
    print(myKnot)

    # swap
    # swap = 0
    # myKnot.swapCrossing(swap)
    # print("\nAfter swapping {}".format(swap))
    # print(myKnot)

    # smooth
    smooth = 0
    myKnot.smoothCrossing(smooth)
    print("\nAfter smoothing {}".format(smooth))
    print(myKnot)

    # print(myKnot.getNAndDir(0, 'i1'))

    

 

    # print(myKnot.computeHomfly())

    ################## -------------- TS5 --------- ##############

    # print("original: ")
    # print(myKnot)

    # smooth 0
    # smooth = 0
    # myKnot.smoothCrossing(smooth)
    # print("\nAfter smoothing {}".format(smooth))
    # print(myKnot)

    # # reduce
    # myKnot.reduceR1s()
    # print("\nAfter reducing")
    # print(myKnot)

    # # swap 1
    # swap = 1
    # myKnot.swapCrossing(swap)
    # print("\nAfter swapping {}".format(swap))
    # print(myKnot)

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