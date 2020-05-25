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
    if len(otherCrossing) > 1:
        print("Error: Found more than one crossing for {}".format(arcType))
        return
    return otherCrossing[0]


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
    while currCrossing != crossingInd2:

        # get the next crossing in direction
        nextCrossing = ijkCrossingNs[currCrossing][currDir]

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
        
        # record findings and proceed
        crossingsFound.append(nextCrossing)
        currCrossing, currDir = nextCrossing, nextDir
    
    # get rid of our destination crossing
    crossingsFound.pop()
    return crossingsFound


# swap a given crossing in-place
def swapCrossing(crossingIndex, ijkCrossings, ijkCrossingNs, handedness):
    i = ijkCrossings[crossingIndex]['i']
    j = ijkCrossings[crossingIndex]['j']
    k = ijkCrossings[crossingIndex]['k']

    # get the endpoints of the i arc, and the other points on j and ks arcs
    iCross0, iCross1 = getOrderedICrossings(crossingIndex, ijkCrossings)
    jCrossOther = getOtherCrossing(crossingIndex, ijkCrossings, 'j')
    kCrossOther = getOtherCrossing(crossingIndex, ijkCrossings, 'k')


    # get the crossings over which the i, j, or k arcs pass through (as i), but
    # don't need to know the crossings between i and iCross1
    # the crossings between inherently are crossings where the arc is i
    i0CrossingsAsI = [
        c for c in getCrossingsBetween(crossingIndex, iCross0, 'i0', ijkCrossings, ijkCrossingNs)
    ]
    jCrossingsAsI =  [
        c for c in getCrossingsBetween(crossingIndex, jCrossOther, 'j', ijkCrossings, ijkCrossingNs)
    ]
    kCrossingsAsI =  [
        c for c in getCrossingsBetween(crossingIndex, kCrossOther, 'k', ijkCrossings, ijkCrossingNs)
    ]

    print("i0CrossingsAsI: {}".format(i0CrossingsAsI))
    print("jCrossingsAsI: {}".format(jCrossingsAsI))
    print("kCrossingsAsI: {}".format(kCrossingsAsI))

    
    # from crossing -> iCross1 stays i's old arcNum, but it's the new k
    newK = i
    # all crossings between crossing -> iCross1 stay constant

    # the new arc formed from iCross0 to crossing steals k's arcNum since
    # k's arcNum will be engulfed by j
    newJ = k

    # update all crossings inbetween crossing and iCross0
    for c in i0CrossingsAsI:
        ijkCrossings[c]['i'] = k
    
    # change the value at iCross0 too
    ijkCrossings[iCross0]['k'] = k

    # j's arcNum extends into k to become the new i
    newI = j

    # update crossings between crossing and other tip of k
    for c in kCrossingsAsI:
        ijkCrossings[c]['i'] = j

    # update the value at tip of k
    ijkCrossings[kCrossOther]['j'] = j

    # the i's on crossings between crossing and other tip of j stay constant
    # as well as the tip of j

    # swap the neighbors
    myNs = ijkCrossingNs[crossingIndex]
    myNs['i0'], myNs['i1'], myNs['j'], myNs['k'] = (
        myNs['j'], myNs['k'], myNs['i0'], myNs['i1']
    )

    # replace our crossing with the new values
    ijkCrossings[crossingIndex] = {'i': newI, 'j': newJ, 'k': newK}

    # # switch the handedness
    handedness[crossingIndex] = "left" if handedness == "right" else "right"


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

print("preswap: ")
print("crossings:")
for i, c in enumerate(ijkCrossings):
    print("  {}: {}".format(i, c))
print("neighbors: ")
for i, c in enumerate(ijkCrossingNs):
    print("  {}: {}".format(i, c))

# test swap crossings
print()
swapCrossing(0, ijkCrossings, ijkCrossingNs, handedness)
print()

print("After swapping")
print("crossings:")
for i, c in enumerate(ijkCrossings):
    print("  {}: {}".format(i, c))
print("neighbors: ")
for i, c in enumerate(ijkCrossingNs):
    print("  {}: {}".format(i, c))

# print(getCrossingsBetween(2, 0, 'i1', ijkCrossings, ijkCrossingNs))

# this is skipping 1 for some reason




# if __name__ == "__main__":
#     from KnotCanvas import main
#     main()







