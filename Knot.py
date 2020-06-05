from sympy import symbols, Matrix
from random import choice
import copy
import json


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
            cData is not None and any([arc == myArc for _, arc in cData.items()])
        ]

        # get the neighbor
        if len(crossingsOnArc) == 1: # single loop back to self
            n = crossingsOnArc[0]
        else: 
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
        currDir = inDir
        hitDest = False
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
                    if myType == "over":
                        if hitDest: # already hit dest once before
                            break
                        else:
                            hitDest = True
                    else: # type is under
                        if myType == "under": 
                            break
                else:
                    break
        
        # get rid of our destination crossing
        crossingsFound.pop()
        return crossingsFound

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

        # get connected arcs
        i0 = self.ijkCrossings[c]['i0']
        i1 = self.ijkCrossings[c]['i1']
        j = self.ijkCrossings[c]['j']
        k = self.ijkCrossings[c]['k']

        # only swap crossings, no need to propogate changes
        self.ijkCrossings[c]['i0'] = j
        self.ijkCrossings[c]['i1'] = k
        self.ijkCrossings[c]['j'] = i0
        self.ijkCrossings[c]['k'] = i1

        # switch the handedness
        self.handedness[c] = {'left': 'right', 'right': 'left'}[self.handedness[c]]

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

        # remove crossing
        self.ijkCrossings[c] = None
        self.handedness[c] = None

        # increase the number of unknots
        self.numUnknots += numSameArcs

    # return an R1 crossing, the crossings between it, the direction in which the
    # loop goes, and the type of all crossings between ('over' or 'under').
    def getR1Crossing(self):

        # for each crossing
            # it's an r1 crossing if, for some path that that it belongs to,
            # for all other knots, that we intersect with, our knot goes over or under
        
        for c in range(len(self.ijkCrossings)):
            if self.ijkCrossings[c] is not None:
                # get all knots this crossing belongs to
                paths = self.getKnotPaths()
                
        
        # check each crossing
        for c in range(len(self.ijkCrossings)):
            if self.ijkCrossings[c] is not None:
                for myDir in ['i0', 'i1']: # try both directions
                    betweens = self.getCrossingsBetween(c, c, myDir)
                    if len(betweens) == 1: # special case we have a link
                        # get all crossings on this entire extended arc
                        print("SPECIAL CASE LINK:")
                        print(self.getCrossingsBetween(c, c, myDir, forceToTip=True))

                    else:
                        # test if they're all over or all under
                        allOver = all([myType == "over" for _, myType in betweens])
                        allUnder = all([myType == "under" for _, myType in betweens])
                        if allOver or allUnder:
                            return (
                                c, 
                                [cr for cr, _ in betweens], # return crossings
                                myDir,
                                "over" if allOver else "under"
                            )
        return None, None, None, None

    # repeatedly reduces all R1 crossings until there are none left
    def reduceR1s(self, numReductions=float("inf")):

        # identify an R1 crossing and remove it via an R1 move
        # we know that the path doesn't contain the same vertex twice
        reduced = 0
        while True:
            print("Reduction #{}".format(reduced + 1))
            c, csBetweenSelf, myDir, pathType = self.getR1Crossing()
            if c is not None and reduced < numReductions:
                for cBetweenSelf in csBetweenSelf + [c]: # must remove c last TODO: CHECK THIS
                    numU = self.numUnknots
                    self.removeCrossing(cBetweenSelf)
                    diff = self.numUnknots - numU
                    if diff == 0:
                        text = ""
                    else:
                        text = " (+{} unknots)".format(diff)
                    print("  - Remove {}{}".format(cBetweenSelf, text))
                reduced += 1
            else:
                print(" - nothing, all done")
                break

    # remove a crossing from a knot diagram, connecting the neighbors to each other
    # it's possible that this puts the diagram in an invalid state
    # could add unknots
    def removeCrossing(self, c):
        # get the arcs
        crossing = self.ijkCrossings[c]
        if crossing is None:
            print("Error: Can't remove a crossing that's already removed")
            return
        i0, i1, j, k = crossing['i0'], crossing['i1'], crossing['j'], crossing['k']

        # this crossing could be the only one left on its knot
        if len(set([i0, i1, j, k])) == 2: # simply increase unknots
            self.numUnknots += 1
        else:
            # if it's just a single loop, we want to take the correct j/k and
            # merge with i1/i0
            if i1 == j:
                self.updateCrossing(c, {
                    'k': i0
                })
            elif i0 == k:
                self.updateCrossing(c, {
                    'i1': j
                })
            else: # not a single loop around to self
                self.updateCrossing(c, {
                    'i1': i0,
                    'k': j
                })

        # remove crossing
        self.ijkCrossings[c] = None
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

    # return all arcs in given knot diagram
    def getArcs(self):
        arcs = set()
        for crossing, crossingData in enumerate(self.ijkCrossings):
            if crossingData is not None:
                for myDir, arc in crossingData.items():
                    arcs.add(arc)
        return arcs

    # returns crossings and incoming dirs on a given arc, in order of direction
    def getArcCrossings(self, arc):
        c1, c2, c1IncDir, c2IncDir = None, None, None, None
        for c in range(len(self.ijkCrossings)):
            if self.ijkCrossings[c] is not None:
                if self.ijkCrossings[c]['i1'] == arc:
                    c1, c1IncDir = c, 'i1'
                if self.ijkCrossings[c]['k'] == arc:
                    c1, c1IncDir = c, 'k'
                if self.ijkCrossings[c]['i0'] == arc:
                    c2, c2IncDir = c, 'i0'
                if self.ijkCrossings[c]['j'] == arc:
                    c2, c2IncDir = c, 'j'
        return c1, c1IncDir, c2, c2IncDir

    # returns all unique (crossing, dir) paths around our knot diagram
    def getKnotPaths(self): 
        def cyclicEquiv(a, b): # credit to stackoverflow user salvador-dali
            if len(a) != len(b):
                return False
            str1 = ' '.join(map(str, a))
            str2 = ' '.join(map(str, b))
            if len(str1) != len(str2):
                return False
            return str1 in str2 + ' ' + str2

        # get all arcs
        arcsToCheck = self.getArcs()

        # keep track of all paths
        paths = []

        for sourceArc in arcsToCheck:

            # create a new knot for this arc
            thisPath = []

            # loop forward until we hit this arc again
            currArc = sourceArc
            while True: # want to go at least once

                # get the next crossing and incoming crossing
                c1, c1OutDir, c2, c2IncDir = self.getArcCrossings(currArc)

                # figure out in which direction to continue searching
                nextDir = {'i0': 'i1', 'i1': 'i0', 'j': 'k', 'k': 'j'}[c2IncDir]

                # get the next arc
                nextArc = self.ijkCrossings[c2][nextDir]

                # record findings
                # thisPath.append((currArc, c2))
                thisPath.append((c1, c1OutDir))
                
                # proceed and break if necessary
                currArc = nextArc
                if currArc == sourceArc:
                    break
            paths.append(thisPath)
            
        # reduce to unique crossing cycles
        uniques = []
        for a in paths:
            exists = False
            for b in uniques:
                if cyclicEquiv(a, b):
                    exists = True
            if not exists:
                uniques.append(a)
        
        return uniques

if __name__ == "__main__":
    # figure 8 knot for testing
    ijkCrossings = [
        {'i0': 3, 'i1': 4, 'j': 6, 'k': 7},
        {'i0': 5, 'i1': 6, 'j': 0, 'k': 1},
        {'i0': 7, 'i1': 0, 'j': 2, 'k': 3},
        {'i0': 1, 'i1': 2, 'j': 4, 'k': 5},
    ]
    handedness = ['left', 'right', 'left', 'right']

    myKnot = Knot(ijkCrossings, handedness)

    print("original: ")
    print(myKnot)

    for p in myKnot.getKnotPaths():
        print(p)

    # smooth
    smooth = 0
    myKnot.smoothCrossing(smooth)
    print("\nAfter smoothing {}".format(smooth))
    print(myKnot)

    for p in myKnot.getKnotPaths():
        print(p)

    # reduce
    myKnot.reduceR1s()
    print("\nAfter reducing")
    print(myKnot)

    for p in myKnot.getKnotPaths():
        print(p)

    # swap
    # swap = 1
    # myKnot.swapCrossing(swap)
    # print("\nAfter swapping {}".format(swap))
    # print(myKnot)

    

    # # reduce
    # myKnot.reduceR1s()
    # print("\nAfter reducing")
    # print(myKnot)


    # # smooth
    # smooth = 1
    # myKnot.smoothCrossing(smooth)
    # print("\nAfter smoothing {}".format(smooth))
    # print(myKnot)

    # # smooth
    # smooth = 3
    # myKnot.smoothCrossing(smooth)
    # print("\nAfter smoothing {}".format(smooth))
    # print(myKnot)

    # # reduce
    # myKnot.reduceR1s()
    # print("\nAfter reducing")
    # print(myKnot)
    

    # then test smooth 1 and reduce



    # # swap
    # swap = 0
    # myKnot.swapCrossing(swap)
    # print("\nAfter swapping {}".format(swap))
    # print(myKnot)

    # # reduce
    # myKnot.reduceR1s()
    # print("\nAfter reducing")
    # print(myKnot)

    # # remove
    # remove = 0
    # myKnot.removeCrossing(remove)
    # print("\nAfter removing {}".format(remove))
    # print(myKnot)

    # # remove
    # remove = 2
    # myKnot.removeCrossing(remove)
    # print("\nAfter removing {}".format(remove))
    # print(myKnot)

    # # remove
    # remove = 1
    # myKnot.removeCrossing(remove)
    # print("\nAfter removing {}".format(remove))
    # print(myKnot)

    # # remove
    # remove = 3
    # myKnot.removeCrossing(remove)
    # print("\nAfter removing {}".format(remove))
    # print(myKnot)


    # # smooth
    # smooth = 0
    # myKnot.smoothCrossing(smooth)
    # print("\nAfter smoothing {}".format(smooth))
    # print(myKnot)



    

 

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