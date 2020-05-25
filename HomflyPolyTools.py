from sympy import symbols, Matrix

# helper function to return the two end-crossings on an arc in
# cyclical order
def getOrderedICrossings(index, ijkCrossings):
    i = ijkCrossings[index]['i']

    # first is the crossing where i = k, second is the crossing where i = j
    first = [
        ind for ind, crossings in enumerate(ijkCrossings) if crossings['k'] == i
    ]
    second = [
        ind for ind, crossings in enumerate(ijkCrossings) if crossings['j'] == i
    ]
    if len(first) > 1 or len(second) > 1:
        print("Error: Found more than one first/second crossing for i")
        return
    return first[0], second[0]

# helper function to return crossing at other end of an arc, only useful for j/k
def getOtherCrossing(index, ijkCrossings, arcType):
    if arcType != "j" and arcType != "k":
        print("Error: Only used for j and k, not {}".format(arcType))
        return
    myArc = ijkCrossings[index][arcType]
    lookingForType = "k" if arcType == "j" else "j"
    otherCrossing = [
        ind for ind, crossings in enumerate(ijkCrossings) if crossings[lookingForType] == myArc
    ]
    crossingsAsI = [
        ind for ind, crossings in enumerate(ijkCrossings) if crossings['i'] == myArc
    ]
    if len(otherCrossing) > 1:
        print("Error: Found more than one crossing for {}".format(arcType))
        return
    return otherCrossing[0], crossingsAsI


def checkArcType(arcType):
    return arcType in ["i0", "i1", "j", "k"]

# return the type (i, j, k), not i0/i1, of an arc given a crossing in which
# it's a part of
def getCrossingArcType(crossingInd, arcNum, ijkCrossings):
    myCrossing = ijkCrossings[crossingInd]
    for arcType, otherArcNum in myCrossing.items():
        if arcNum == otherArcNum:
            return arcType
    return None

# returns the arcType in which to depart the crossingN in order to continue
# in the same direction from crossingInd -> crossingN onwards
def getContinuousDir(crossingInd, crossingN, ijkCrossings, ijkCrossingNs):
    # get the arcNum that both crossings share
    sharedArcNum = [
        a for a in ijkCrossings[crossingInd].values() if a in ijkCrossings[crossingN].values()
    ][0]

    print("The shared arcNum between {} and {} is {}".format(crossingInd, crossingN, sharedArcNum))

    # figure incoming direction into crossingN
    incomingDir = getCrossingArcType(crossingN, sharedArcNum, ijkCrossings)
    print("calculated again incoming direction into {}, which is {}".format(crossingN, incomingDir))

    # figure out in which direction to continue
    if incomingDir == 'i': # not clear if i0 or i1, gotta just manually check
        if ijkCrossingNs[crossingN]['i0'] == crossingInd:
            return 'i1' # cus choosing i0 results in going back to first crossing
        elif ijkCrossingNs[crossingN]['i1'] == crossingInd:
            return 'i0'
    else:
        return {'j': 'k', 'k': 'j'}[incomingDir]

# returns the incoming direction from c1 into c2 given outgoing dir from c1
# you need an outgoing dir because it's possible that crossings are connected
# via multiple directions
def getIncomingDir(c1, outDir, c2, ijkCrossings, ijkCrossingNs):
    # error check
    if ijkCrossingNs[c1][outDir] != c2:
        print("Error: C1 -> outdir didn't lead to C2")
        return
    
    # simplify direction to i if it's i0/i1
    modifiedDir = "i" if outDir == "i0" or outDir == "i1" else outDir

    # get the arcNum on which we departed from c1 and arrived onto c2
    arrivalArc = ijkCrossings[c1][modifiedDir]

    # the incoming direction is the dir which is the incoming arc
    return getCrossingArcType(c2, arrivalArc, ijkCrossings)


# return the crossings between crossing1 -> crossing2 in the inDir (i0/1, j, or k)
# direction
def getCrossingsBetween(crossingInd1, crossingInd2, inDir, ijkCrossings, ijkCrossingNs):
    # keep track of crossings inbetween
    crossingsFound = []

    # keep going until we hit our destination crossing
    currCrossing = crossingInd1
    currDir = inDir # i0, i1, j, or k
    print("Starting at {} with dir {}".format(currCrossing, currDir))
    while currCrossing != crossingInd2:
        print("examining crossing {} by looking in dir {}".format(currCrossing, currDir))

        # get the next crossing in direction
        nextCrossing = ijkCrossingNs[currCrossing][currDir]
        crossingsFound.append(nextCrossing)
        print("recorded neighbor {}".format(nextCrossing))

        # get the incoming direction into the neighbor crossing
        incomingDir = getIncomingDir(currCrossing, currDir, nextCrossing, ijkCrossings, ijkCrossingNs)
        

        # figure out in which direction to continue searching
        if incomingDir == 'i': # not clear if i0 or i1, gotta just manually check
            if ijkCrossingNs[nextCrossing]['i0'] == currCrossing:
                nextDir = 'i1' # cus choosing i0 results in going back to first crossing
            elif ijkCrossingNs[nextCrossing]['i1'] == currCrossing:
                nextDir = 'i0'
        else:
            nextDir = {'j': 'k', 'k': 'j'}[incomingDir]
        
        print("continuing in dir {}".format(nextDir))
        currCrossing, currDir = nextCrossing, nextDir
    
    # get rid of our destination crossing
    crossingsFound.pop()
    return crossingsFound


# swap a given crossing in-place
def swapCrossing(crossingIndex, ijkCrossings, ijkCrossingNs, handedness):
    i = ijkCrossings[crossingIndex]['i']
    j = ijkCrossings[crossingIndex]['j']
    k = ijkCrossings[crossingIndex]['k']
    right = handedness == "right"

    # get the endpoints of the i arc, and the other points on j and ks arcs
    iCross1, iCross2, iCrossingsAsI = getOrderedICrossings(crossingIndex, ijkCrossings)
    jCrossOther, jCrossingsAsI = getOtherCrossing(crossingIndex, ijkCrossings, 'j')
    kCrossOther, kCrossingsAsI = getOtherCrossing(crossingIndex, ijkCrossings, 'k')

    
    # i's end is i's arcNum, i's second crossing remains constant
    newK = i

    # all crossings on the second half of i where i is the i for that crossing
    # stay constant

    # the new arc formed in the first half of i steals k's arcNum because j's
    # arcnum will extend into k and become i
    newJ = k
    ijkCrossings[iCross1]['k'] = newJ

    # all crossings between this crossing and the crossing on the prev of old i
    # in the i direction
    # that have old i as an i for them too need to be updated to reflect that 
    # their new i should be k

    # j's arcNum extends into k
    newI = j

    ijkCrossings[jCrossOther]['k'] = newI
    # all crossings between this and jOther in the j direction where oldj is the
    # i in that crossing need to be updated so that their i is newI

    ijkCrossings[kCrossOther]['j'] = newI
    # all crossings between this and kOther in the k direction where oldk is the
    # i in that crossing need to be updated so that their i is newI

    # switch the handedness
    handedness[crossingIndex] = "left" if right else "right"


# smooth a given crossing in-place
def smoothCrossing(crossingIndex, ijkCrossings, handedness):
    pass


# returns true if our current diagram is the unlink
def diagramIsUnLink(ijkCrossings, handedness):
    pass


def compute(ijkCrossings, ijkCrossingNs, handedness):
    pass


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

# print("preswap: ")
# for c in ijkCrossings:
#     print("  {}".format(c))

# # test swap crossings
# swapCrossing(0, ijkCrossings, ijkCrossingNs, handedness)

# print("After swapping crossing 0: ")
# for c in ijkCrossings:
#     print("  {}".format(c))
# print(handedness)

print(getCrossingsBetween(0, 3, 'j', ijkCrossings, ijkCrossingNs))

# this is skipping 1 for some reason




# if __name__ == "__main__":
#     from KnotCanvas import main
#     main()







