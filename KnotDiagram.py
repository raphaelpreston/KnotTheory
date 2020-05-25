from Knot import Knot

class KnotDiagram:
    def __init__(self, ijkCrossings, ijkCrossingNs, handedness):
        self.knots = [Knot(ijkCrossings, ijkCrossingNs, handedness)]

    # returns # of components if our current diagram is an unlink, else false
    def isUnLink(self):
        pass

