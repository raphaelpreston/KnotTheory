from sympy import symbols, Matrix
import copy

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
            print(" - Found {}".format((nextCrossing, myType)))
            currCrossing, currDir = nextCrossing, nextDir

            # break if necessary
            if currCrossing == c2:
                print(" - Hit c2 {} with dir {}".format(currCrossing, myType))
                if forceToTip:
                    if myType == "under": # only break when the arc ends
                        print("breaking")
                        break
                else:
                    break
        
        # get rid of our destination crossing
        crossingsFound.pop()
        print("Crossings between {} and {} in {} dir are {}".format(c1, c2, inDir, crossingsFound))
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
        if self.ijkCrossingNs[c2]['i1'] == c2 and c1 != c2:
            # impossible for the i1 neighbor to be itself and NOT loop back onto
            # self
            print("special case 1")
            v = 'i0' if c1 != c2 else "j"
        elif self.ijkCrossingNs[c2]['i0'] == c2 and c1 != c2:
            v = 'i1'
            print("special case 2")
        else:
            # return necessary
            v = {
                'i0': 'k' if iCross0 == i0N else 'i1',
                'i1': 'j' if iCross1 == i1N else 'i0',
                'j': 'k' if jCrossOther == jN else 'i1',
                'k': 'j' if kCrossOther == kN else 'i0'
            }[outDir]

        print("The incoming dir from {} -{}-> {} is {}".format(c1, outDir, c2, v))
        return v

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

        # update the neighbors
        myNs = self.ijkCrossingNs[crossingIndex]
        myNs['i0'], myNs['i1'], myNs['j'], myNs['k'] = (
            myNs['j'], myNs['k'], myNs['i0'], myNs['i1']
        )

        # replace our crossing with the new values
        self.ijkCrossings[crossingIndex] = {'i': newI, 'j': newJ, 'k': newK}

        # switch the handedness
        self.handedness[crossingIndex] = "left" if self.handedness == "right" else "right"

    # smooth a given crossing in-place, could increase self.numUnknots
    def smoothCrossing(self, c):
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

        # have to save changes locally and then commit them after all changes for
        # incoming direction to work in getCrossingsBetween
        ijkCrossings = copy.deepcopy(self.ijkCrossings)

        # k arc becomes i
        # update the crossings on k
        for cBetween, _ in self.getCrossingsBetween(c, kCrossOther, 'k'):
            ijkCrossings[cBetween]['i'] = i
        
        # update the other end of k
        ijkCrossings[kCrossOther]['j'] = i

        # i1 arc becomes j
        # update the crossings on i1
        for cBetween, _ in self.getCrossingsBetween(c, iCross1, 'i1'):
            ijkCrossings[cBetween]['i'] = j

        # update the other end of i1
        ijkCrossings[iCross1]['j'] = j

        # commit ijkCrossing after all changes have been made
        self.ijkCrossings = ijkCrossings

        # connect neighbors between jN -> i1 curve
        self.ijkCrossingNs[jN][jNIncDir] = i1N
        self.ijkCrossingNs[i1N][i1NIncDir] = jN

        # connect neighbors between i0 -> k curve
        self.ijkCrossingNs[i0N][i0NIncDir] = kN
        self.ijkCrossingNs[kN][kNIncDir] = i0N

        # determine if we've just made an uknot
        print("Before deleting:")

        # remove crossing from ijkCrossings, and handedness
        self.ijkCrossings[c] = None
        self.ijkCrossingNs[c] = None
        self.handedness[c] = None

    # return an R1 crossing and the crossings between it, or None if none exist.
    # guaranteed to not return a crossing in a direction with a path with a vertex
    # that appears twice
    def getR1Crossing(self):
        # first ensure there aren't trivially R1 crossings with the same arc
        # entering the crossing twice. also, existence will break code below
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
                    jOrKN, _ = self.ijkCrossingNs[crossing][jOrK]

                    # loop goes in i1 direction or i0 direction depending
                    dirToSearch = {"j": "i1", "k": "i0"}[jOrK]
                    
                    # shortcut to get crossings between. can't call using crossing
                    # twice because incDir won't work on crossing. < dunno bout this anymore
                    between = self.getCrossingsBetween(crossing, jOrKN, dirToSearch)

                    return (crossing,
                        [c for c, _ in between] + [jOrKN],
                        dirToSearch,
                        "over"
                    )

        # then, all crossings between a given crossing must be "under"
        for crossing in range(len(self.ijkCrossings)):
            ijk = self.ijkCrossings[crossing]
            if ijk is not None:
                for myDir in ['i0', 'i1']: # try both directions
                    between = self.getCrossingsBetween(crossing, crossing, myDir)
                    if all([myType == "under" for _, myType in between]):
                        return (
                            crossing, 
                            [c for c, _ in between], # only care about crossings
                            myDir,
                            "under"
                        )
        return None, None, None

    # repeatedly reduces all R1 crossings until there are none left
    def reduceR1s(self):

        # identify an R1 crossing and remove it via an R1 move
        r1Crossing, csBetweenSelf, myDir = self.getR1Crossing()
        print(r1Crossing, csBetweenSelf, myDir)
        # we know that the path doesn't contain the same vertex twice
        # if the path goes all "over", then all we have to do is remove crossings
        # and adjust neighbors, no connecting has to be done
        
        # remove each crossing on the path
        # for cBetween in csBetweenSelf:
        if True:
            cBetween = csBetweenSelf[0]

            # each crossing has a single partner crossing. all crossings are unique.
            # the path either goes over all crossings or under all crossings.

            # if "over", set k and j neighbors to be their own neighbors
            # if "under", set i1 and i0 neighbors to be neighbors

            # remove the crossing


            # find the crossing's partner crossing aka where it leaves the loop again
            # if the type is "over", then the partner is in the k direction,
            # if it's "under", then the partner is in the i1 direction

            # find the neighbors to the outside of the loop for each set of partners

            # find the immediate neighbors inside of the loop (between the partners)

            # the outside neighbor(s) (maybe the they're the same) need their neighbors
            # to become the neighbors inside the loop. if there are no neighbors
            # inside the loop then they become neighbors of each other

            # if outside neighbors are the same, then that neighbor's
            # neighbor becomes itself (in 2 directions)

            # remove both partner crossings
            self.removeCrossing(cBetween)

    # remove a crossing from a knot diagram, connecting the neighbors to each other
    # it's possible that this puts the diagram in an invalid state
    def removeCrossing(self, c):
        # get the arcs
        crossing = self.ijkCrossings[c]
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
            if kN == c:
                ijkCrossingNs[jN][jNInc] = self.ijkCrossingNs[c]['i1']
                print("0: Setting crossingNs[{}][{}] = {}".format(jN, jNInc, self.ijkCrossingNs[c]['i1']))
            else:
                ijkCrossingNs[jN][jNInc] = kN
                print("0: Setting crossingNs[{}][{}] = {}".format(jN, jNInc, kN))
            
            if jN == c:
                ijkCrossingNs[kN][kNInc] = self.ijkCrossingNs[c]['i0']
                print("1: Setting crossingNs[{}][{}] = {}".format(kN, kNInc, self.ijkCrossingNs[jN]['i0']))
            else:
                ijkCrossingNs[kN][kNInc] = jN
                print("1: Setting crossingNs[{}][{}] = {}".format(kN, kNInc, jN))
            
            if i1N == c:
                ijkCrossingNs[i0N][i0NInc] = self.ijkCrossingNs[c]['k']
                print("2: Setting crossingNs[{}][{}] = {}".format(i0N, i0NInc, self.ijkCrossingNs[c]['k']))
            else:
                ijkCrossingNs[i0N][i0NInc] = i1N
                print("2: Setting crossingNs[{}][{}] = {}".format(i0N, i0NInc, i1N))
            
            if i0N == c:
                ijkCrossingNs[i1N][i1NInc] = self.ijkCrossingNs[c]['j']
                print("3: Setting crossingNs[{}][{}] = {}".format(i1N, i1NInc, self.ijkCrossingNs[c]['j']))
            else:
                ijkCrossingNs[i1N][i1NInc] = i0N
                print("3: Setting crossingNs[{}][{}] = {}".format(i1N, i1NInc, i0N))
        
        # commit local crossing and neighbor changes
        self.ijkCrossings = ijkCrossings
        self.ijkCrossingNs = ijkCrossingNs

        # remove crossing
        self.ijkCrossings[c] = None
        self.ijkCrossingNs[c] = None
        self.handedness[c] = None

if __name__ == "__main__":


    # figure 8 knot for testing
    ijkCrossings = [
        {'i': 2, 'j': 3, 'k': 0},
        {'i': 3, 'j': 0, 'k': 1},
        {'i': 0, 'j': 1, 'k': 2},
        {'i': 1, 'j': 2, 'k': 3}
    ]
    # ijkCrossingNs = [
    #     {'i0': (2, 'k'), 'i1': (3, 'j'), 'j': (1, 'i1'), 'k': (2, 'i0')},
    #     {'i0': (3, 'k'), 'i1': (0, 'j'), 'j': (2, 'i1'), 'k': (3, 'i0')},
    #     {'i0': (0, 'k'), 'i1': (1, 'j'), 'j': (3, 'i1'), 'k': (0, 'i0')},
    #     {'i0': (1, 'k'), 'i1': (2, 'j'), 'j': (0, 'i1'), 'k': (1, 'i0')},
    # ]
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
        print("Handedness: {}".format(myKnot.handedness))
        print("Unknots: {}".format(myKnot.numUnknots))

    print("original: ")
    printStuff()

    # print(myKnot.getNAndDir(0, 'i1'))

    # test smooth crossings
    # smooth = 0
    # myKnot.smoothCrossing(smooth)
    # print("\nAfter smoothing {}".format(smooth))
    # printStuff()

    # test swap crossings
    swap = 0
    myKnot.swapCrossing(swap)
    print("\nAfter swapping {}".format(swap))
    printStuff()


    # test removal
    remove = 0
    myKnot.removeCrossing(remove)
    print("After removing {}".format(remove))
    printStuff()

    # test removal
    remove = 2
    myKnot.removeCrossing(remove)
    print("After removing {}".format(remove))
    printStuff()

    # test removal
    remove = 1
    myKnot.removeCrossing(remove)
    print("After removing {}".format(remove))
    printStuff()

    # test smooth crossings
    # smooth = 1
    # myKnot.smoothCrossing(smooth)

    # print("\nAfter smoothing {}".format(smooth))
    # printStuff()

    # test R1 reduction
    # print()
    # myKnot.reduceR1s()
    # print("After reduce R1s:")
    # printStuff()

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