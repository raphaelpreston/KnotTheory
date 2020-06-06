from KnotCanvas import main


# get the list of knots and their filenamese
fnames = []
with open('filenames.txt') as f:
    for line in f:
        fnames.append(line.strip())

# limit test to a certain amount
testLimit = 9000
print("Calculating HOMFLY polynomial for {} knots".format(testLimit))

# start with some knot
knot = None
startInd = 0 if knot is None else fnames.index('{}.png'.format(knot))

for fname in fnames[startInd:startInd + testLimit]:
    print('-----------------------------{}---------------------------'.format(fname))
    try:
        main('local_knot_data/knotinfo/{}'.format(fname))
    except Exception as e:
        with open("homfly_out.csv", 'a+') as f:
            f.write("{},{}\n".format(fname, e))