from sympy import symbols, Matrix

# swap a given crossing in-place
def swapCrossing(crossingIndex, ijkCrossings, handedness):
    i = ijkCrossings[crossingIndex]['i']
    j = ijkCrossings[crossingIndex]['j']
    k = ijkCrossings[crossingIndex]['k']
    right = handedness == "right"

    # j and k both become i

    # i splits into j and k


# smooth a given crossing in-place
def smoothCrossing(crossingIndex, ijkCrossings, handedness):
    pass


# returns true if our current diagram is the unlink
def diagramIsUnLink(ijkCrossings, handedness)
    pass


def compute(ijkCrossings, handedness):
    pass


# figure 8 knot for testing
ijkCrossings = [
    {'i': 2, 'j': 3, 'k': 0},
    {'i': 3, 'j': 0, 'k': 1},
    {'i': 0, 'j': 1, 'k': 2},
    {'i': 1, 'j': 2, 'k': 3}
]
handedness = ['left', 'right', 'left', 'right']

# test swap crossings
swapCrossing(0, ijkCrossings, handedness)
print("After swapping crossing 0: ")
print(ijkCrossings)
print(handedness)





# if __name__ == "__main__":
#     from KnotCanvas import main
#     main()







