from KnotCanvas import main


# get the list of knots and their filenames
fnames = []
with open('filenames.txt') as f:
    for line in f:
        fnames.append(line.strip())

# limit test to a certain amount
testLimit = 10
print("Calculating HOMFLY polynomial for {} knots".format(testLimit))

# start with some knot
knot = None
startInd = 0 if knot is None else fnames.index('{}}.png'.format(knot))

for fname in fnames[startInd:testLimit]:
    print('-----------------------------{}---------------------------'.format(fname))
    main('local_knot_data/knotinfo/{}'.format(fname))