from Knot import Knot

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

myKnot = Knot(ijkCrossings, ijkCrossingNs, handedness)

print("preswap: ")
print("crossings:")
for i, c in enumerate(myKnot.ijkCrossings):
    print("  {}: {}".format(i, c))
print("neighbors: ")
for i, c in enumerate(myKnot.ijkCrossingNs):
    print("  {}: {}".format(i, c))

# test swap crossings
print()
swap = 0
myKnot.swapCrossing(swap)
print()

print("After swapping {}".format(swap))
print("crossings:")
for i, c in enumerate(myKnot.ijkCrossings):
    print("  {}: {}".format(i, c))
print("neighbors: ")
for i, c in enumerate(myKnot.ijkCrossingNs):
    print("  {}: {}".format(i, c))

# print(getCrossingsBetween(2, 0, 'i1', ijkCrossings, ijkCrossingNs))

# this is skipping 1 for some reason




# if __name__ == "__main__":
#     from KnotCanvas import main
#     main()







