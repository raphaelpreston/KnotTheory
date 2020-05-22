from sympy import symbols, Matrix, expand

# printing method adapted from
# https://stackoverflow.com/questions/13214809/pretty-print-2d-python-list
def pm(A):
    if type(A) is Matrix:
        A = A.tolist()
    print('\n'.join(['\t'.join([str(cell) for cell in row]) for row in A]))


def getMatrix(ijkCrossings, handedness):
    # initialize matrix
    n = len(ijkCrossings) # same as number of arcs
    A = [[0 for _ in range(n)] for _ in range(n)]
    t = symbols('t')

    # each row corresponds to a crossing
    for crossingNum in range(n):
        row = A[crossingNum]
        i = ijkCrossings[crossingNum]["i"]
        j = ijkCrossings[crossingNum]["j"]
        k = ijkCrossings[crossingNum]["k"]

        # put 1-t in the ith col
        row[i] = 1-t
        if handedness[crossingNum] == "right":
            row[j] = -1 # -1 in jth col
            row[k] = t # t in kth col
        elif handedness[crossingNum] == "left":
            row[j] = t # t in jth col
            row[k] = -1 # -1 in kth col
        else:
            print("Error: Unrecognized handedness.")
            return

    # remove last row and column to get Alexander Matrix
    aMat = Matrix(A)
    aMat.col_del(n-1)
    aMat.row_del(n-1)
    return aMat


def compute(ijkCrossings, handedness):

    matrix = getMatrix(ijkCrossings, handedness)
    print("Alexander Matrix:")
    pm(matrix)

    return expand(matrix.det())


if __name__ == "__main__":
    from KnotCanvas import main
    main()

