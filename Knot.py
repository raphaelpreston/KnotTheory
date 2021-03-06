from sympy import symbols, Matrix, expand
from sympy import latex as latexForm
from random import choice
import copy
import json

class RecError(Exception):
    pass

class Knot:
    def __init__(self, ijkCrossings, handedness, numUnknots=0, name="", ijkCrossingNs=None):
        print() #######################
        # convert from i, j, k crossings into i0, i1, j, k 
        nextNum = len(ijkCrossings) # number of arcs is same as number of crossings
        if ijkCrossingNs is not None:
            # for every crossing
            for c in range(len(ijkCrossings)):
                # get i0 neighbor and the incoming direction into said neighbor
                i = ijkCrossings[c]['i']
                j = ijkCrossings[c]['j']
                k = ijkCrossings[c]['k']
                i0N, i0NIncDir = ijkCrossingNs[c]['i0']

                # update self
                ijkCrossings[c] = {
                    'i0': nextNum,
                    'i1': i,
                    'j': j,
                    'k': k
                }

                # update neighbor behind me
                ijkCrossings[i0N][i0NIncDir] = nextNum

                nextNum += 1
        
        self.ijkCrossings = ijkCrossings
        self.handedness = handedness
        self.numUnknots = numUnknots
        self.name = name

        
    

    def __str__(self):
        s = "---- Knot {}({}) ----\n".format(
            "{} ".format(self.name),
            hex(id(self))
        )
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
        
        # check if there are R1 crossings to resolve between links
        inters = {} # path 1 => path2: way it crosses over
        for c in range(len(self.ijkCrossings)):
            if self.ijkCrossings[c] is not None:

                # get all knots this crossing belongs to
                myPaths = self.getCrossingPaths(c)

                # check all of crossing's paths against each other
                for path1Ind, path1 in enumerate(myPaths):
                    # keep track of each path we hit and whether we go under or over
                    for path2Ind, path2 in enumerate(myPaths):
                        if path1 != path2: # two paths intersect at crossing c
                            # convert both paths to over/under style
                            p1C = {
                                cr: "over" if myDir in ['i0', 'i1'] else "under"
                                for cr, myDir in path1
                            }
                            # crossings with a loop will be overriden but that's okay,
                            # crossings with a loop can't be a link
                            
                            if path1Ind in inters:
                                inters[path1Ind][path2Ind].append((c, p1C[c]))
                            else:
                                inters[path1Ind] = {path2Ind: [(c, p1C[c])]}

        # check any intersections
        for path1Ind, path1 in inters.items():
            for path2Ind, cs in path1.items():
                styles = [style for _, style in cs]
                if all([style == styles[0] for style in styles]):
                    # any shared crossing between the paths can be removed
                    return cs[0][0], [], None, None


        # if you can't move links apart, then any R1 moves will be twisted, 
        # and we can detect as follows
        
        # check each crossing
        for c in range(len(self.ijkCrossings)):
            if self.ijkCrossings[c] is not None:
                for myDir in ['i0', 'i1']: # try both directions
                    betweens = self.getCrossingsBetween(c, c, myDir)
                    if len(betweens) != 1: # link R2 crossings already ruled out
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

        # increase unknots
        if i0 == i1 and j == k: # last connection btwn two links
            self.numUnknots += 2
        if i0 == k and i1 == j: # just a twisted unknot
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
    def duplicate(self, name=None):
        return Knot(
            copy.deepcopy(self.ijkCrossings),
            copy.deepcopy(self.handedness),
            self.numUnknots,
            name=self.name if name is None else name
        )

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

    # returns all paths that a given crossing belongs to
    def getCrossingPaths(self, c):
        myPaths = []
        for path in self.getKnotPaths():
            for cr, _ in path:
                if cr == c:
                    myPaths.append(path)
                    break
        return myPaths

    # internal recursive function for computing homfly
    def _homfly(self, k, l, m, depth, depthLim, crossingsDist):
        print("{}: computing HOMFLY:".format(k.name))

        # reduce all R1 crossings out of our knot
        k.reduceR1s()
        k.name += "m"
        print()
        print(k)

        # reached recursion limit
        if depth >= depthLim:
            raise RecError("Reached recursion limit")

        # base case: k is an unlink of n components
        if k.isUnlink():
            n = k.numUnknots
            poly = (-m**-1)**(n-1) * (l + l**(-1))**(n-1)
            print("{}: hit basecase, n={}:  {}".format(k.name, n, poly))
            return poly

        # get our distinguished crossing
        print("Distinguished so far: {}".format(crossingsDist))
        validCrossings = [
            i for i, c in enumerate(k.ijkCrossings)
            if c is not None and i not in crossingsDist
        ]
        validCrossings.sort()
        distCrossing = validCrossings[0]
        isRight = {'right': True, 'left': False}[k.handedness[distCrossing]]

        # mark crossing as distinguished so it doesn't happen again
        crossingsDist.add(distCrossing)
        
        # copy knot, append modification to name
        kR, kL, kS = k.duplicate(), k.duplicate(), k.duplicate()
        kR.name += "r"
        kL.name += "l"
        kS.name += "s"

        # modify accordingly
        if isRight:
            print("{}: swapping '{}' from right to left to get {}".format(k.name, distCrossing, kL.name))
            kL.swapCrossing(distCrossing)
        else:
            print("{}: swapping '{}' from left to right to get {}".format(k.name, distCrossing, kR.name))
            kR.swapCrossing(distCrossing)
        print("{}: smoothing '{}' to get {}".format(k.name, distCrossing, kS.name))
        kS.smoothCrossing(distCrossing)

        print()
        if isRight:
            print(kL)
        else:
            print(kR)
        print(kS)

        # compute necessary polynomials
        if isRight:
            pL = self._homfly(kL, l, m, depth + 1, depthLim, copy.deepcopy(crossingsDist))
            print("{}: solved: {}".format(kL.name, pL))
        else:
            pR = self._homfly(kR, l, m, depth + 1, depthLim, copy.deepcopy(crossingsDist))
            print("{}: solved: {}".format(kR.name, pR))
        pS = self._homfly(kS, l, m, depth + 1, depthLim, copy.deepcopy(crossingsDist))
        print("{}: solved: {}".format(kS.name, pS))

        # return equation solved for the correct polynomial
        if isRight:
            v = (-m * pS - l**-1 * pL) / l
        else:
            v = (-m * pS - l * pR) * l
        ex = expand(v)
        print("{}: returning {} => {}".format(k.name, v, ex))
        return ex

    # recursively compute the homfly polynomial
    # set latex to true to format it latex style
    def computeHomfly(self, latex=False, depthLim=float('inf')):

        # share symbols with all new knots' equations
        l, m = symbols("l m")

        try:
            homfly = self._homfly(self.duplicate(name="K"), l, m, 0, depthLim, set())
            return latexForm(homfly) if latex else homfly
        except RecError:
            return "Recursion Error"
        except IndexError:
            return "Ran out of crossings to distinguish"
        except Exception as e:
            return e


if __name__ == "__main__":
    # from KnotCanvas import main
    # main()

    # another taurus
    ijkCrossings = [
        {'i0': 7, 'i1': 1, 'j': 2, 'k': 11},
        {'i0': 8, 'i1': 3, 'j': 0, 'k': 12},
        {'i0': 9, 'i1': 6, 'j': 5, 'k': 13},
        {'i0': 10, 'i1': 2, 'j': 4, 'k': 7},
        {'i0': 11, 'i1': 0, 'j': 1, 'k': 8},
        {'i0': 12, 'i1': 5, 'j': 3, 'k': 9},
        {'i0': 13, 'i1': 4, 'j': 6, 'k': 10}
    ]
    handedness = ['right', 'right', 'right', 'right', 'right', 'right', 'right']

    myKnot = Knot(ijkCrossings, handedness)

    print(myKnot.computeHomfly())

    # # taurus
    # ijkCrossings = [
    #     {'i0': 5, 'i1': 1, 'j': 0, 'k': 8},
    #     {'i0': 6, 'i1': 3, 'j': 4, 'k': 9},
    #     {'i0': 7, 'i1': 0, 'j': 2, 'k': 5},
    #     {'i0': 8, 'i1': 4, 'j': 1, 'k': 6},
    #     {'i0': 9, 'i1': 2, 'j': 3, 'k': 7}
    # ]
    # handedness = ['right', 'right', 'right', 'right', 'right']

    # myKnot = Knot(ijkCrossings, handedness)

    # print(myKnot.computeHomfly())

    # # figure 8 knot
    # ijkCrossings = [
    #     {'i0': 3, 'i1': 4, 'j': 6, 'k': 7},
    #     {'i0': 5, 'i1': 6, 'j': 0, 'k': 1},
    #     {'i0': 7, 'i1': 0, 'j': 2, 'k': 3},
    #     {'i0': 1, 'i1': 2, 'j': 4, 'k': 5},
    # ]
    # handedness = ['left', 'right', 'left', 'right']

    # trefoil
    # ijkCrossings = [
    #     {'i0': 2, 'i1': 3, 'j': 5, 'k': 0},
    #     {'i0': 0, 'i1': 1, 'j': 3, 'k': 4},
    #     {'i0': 4, 'i1': 5, 'j': 1, 'k': 2},
    # ]
    # handedness = ['right', 'right', 'right']

    # myKnot = Knot(ijkCrossings, handedness)

    # print(myKnot.computeHomfly())




    # print("original: ")
    # print(myKnot)

    # # swap
    # swap = 0
    # myKnot.swapCrossing(swap)
    # print("\nAfter swapping {}".format(swap))
    # print(myKnot)

    # print(myKnot.getR1Crossing())



    # # smooth
    # smooth = 0
    # myKnot.smoothCrossing(smooth)
    # print("\nAfter smoothing {}".format(smooth))
    # print(myKnot)

    # # reduce
    # myKnot.reduceR1s()
    # print("\nAfter reducing")
    # print(myKnot)

    # # swap
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