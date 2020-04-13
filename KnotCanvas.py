# The heart of the operation: displays and runs everything

import sys
import os
from math import sin, cos, radians
from random import randint
from LineFinder import *
from skimage import io
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QGridLayout, QWidget
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont, QPen
from PyQt5.QtCore import Qt, QTimer

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

class KnotCanvas(QWidget):

    def __init__(self, fileName, tickFPS):
        super().__init__()

        # declare class variables
        self.fileName = fileName
        self.imageData = io.imread(fileName) # get image data with sci-kit
        self.lf = LineFinder(self.imageData, x=randint(150,450),
            y=randint(150, 450), degreeRot=randint(0,359), displayType='arrow') # initialize LineFinder

        # boilerplate to add image background
        self.im = QPixmap(fileName)
        self.label = QLabel()
        self.label.setPixmap(self.im)
        self.grid = QGridLayout()
        self.grid.addWidget(self.label, 1, 1)
        self.setLayout(self.grid)

        # set window meta info
        self.setGeometry(200, 150, 1, 1)
        self.setWindowTitle("Knot Analysis")
        self.show()

        # begin frame-by-frame refresh timer
        timer = QTimer(self, timeout=self.doTick, interval=1000/tickFPS)
        timer.start()

    # boilderplate for a frame update
    def doTick(self):
        self.tickLogic() # perform each tick logic
        self.update() # re-run paintEvent()

    # boilerplate to handle frame-by-frame updates
    def paintEvent(self, event):
        self.im = QPixmap(self.fileName) # reset background
        self.label.setPixmap(self.im)
        qp = QPainter() # start painting
        qp.begin(self.im)
        self.draw(qp)
        qp.end()
        self.label.setPixmap(self.im) # update image with painting on top

    # perform the logic for each frame update
    def tickLogic(self):
        self.lf.getNextPosition() # set the linefinder's next position # TODO: could make this a linefinder.dotick or something

    # paint the stuff each tick
    def draw(self, qp):
        pen = QPen(Qt.red, 2, Qt.SolidLine)
        qp.setPen(pen)
        self.lf.drawLineFinder(qp) # draw the linefinder

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = KnotCanvas('knot.png', 15)
    sys.exit(app.exec_())