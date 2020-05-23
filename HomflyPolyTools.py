from sympy import symbols, Matrix

# helper function to return the two crossing indices on an arc in cyclical order
# AND all the crossings over which the given arc crosses as 'i' (besides itself)
def getOrderedICrossings(index, ijkCrossings):
    i = ijkCrossings[index]['i']

    # first is the crossing where i = k, second is the crossing where i = j
    first = [
        ind for ind, crossings in enumerate(ijkCrossings) if crossings['k'] == i
    ]
    second = [
        ind for ind, crossings in enumerate(ijkCrossings) if crossings['j'] == i
    ]
    crossingsAsI = [
        ind for ind, crossings in enumerate(ijkCrossings)
        if crossings['i'] == i and ind != index
    ]
    if len(first) > 1 or len(second) > 1:
        print("Error: Found more than one first/second crossing for i")
        return
    return first[0], second[0], crossingsAsI

# helper function to return other crossing that has the given arcNum
# AND all the crossings over which the given arc crosses as 'i'
# only used for j and k arcTypes
def getOtherCrossing(index, ijkCrossings, arcType):
    if arcType != "j" and arcType != "k":
        print("Error: Unrecognized arc type {}".format(arcType))
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

# swap a given crossing in-place
def swapCrossing(crossingIndex, ijkCrossings, ijkCrossingNs, handedness):
    i = ijkCrossings[crossingIndex]['i']
    j = ijkCrossings[crossingIndex]['j']
    k = ijkCrossings[crossingIndex]['k']
    crossingNs = ijkCrossingNs[crossingIndex]
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
    {'i': {'next': 3, 'prev': 2}, 'j': 1, 'k': 2},
    {'i': {'next': 0, 'prev': 3}, 'j': 2, 'k': 3},
    {'i': {'next': 1, 'prev': 0}, 'j': 3, 'k': 0},
    {'i': {'next': 2, 'prev': 1}, 'j': 0, 'k': 1}
]
handedness = ['left', 'right', 'left', 'right']

print("preswap: ")
for c in ijkCrossings:
    print("  {}".format(c))

# test swap crossings
swapCrossing(0, ijkCrossings, ijkCrossingNs, handedness)

print("After swapping crossing 0: ")
for c in ijkCrossings:
    print("  {}".format(c))
print(handedness)





# if __name__ == "__main__":
#     from KnotCanvas import main
#     main()







