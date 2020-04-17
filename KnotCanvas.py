# The heart of the operation: displays and runs everything

import sys
import os
from math import sin, cos, radians
from random import randint
from LineFinder import *
from KnotHandler import *
from skimage import io, color, morphology, img_as_float
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QGridLayout, QWidget
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont, QPen
from PyQt5.QtCore import Qt, QTimer

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

class KnotCanvas(QWidget):

    def __init__(self, fileName, tickFPS):
        super().__init__()

        # skeletonize image
        image = img_as_float(color.rgb2gray(io.imread('knot.png')))
        image_binary = image < 0.5
        self.skelImageData = morphology.skeletonize(image_binary)

        # declare class variables
        self.fileName = fileName
        self.imageData = io.imread(fileName) # get image data with sci-kit
        self.kh = KnotHandler(self.imageData, self.skelImageData)

        # boilerplate to add image background
        self.im = QPixmap(fileName)
        self.label = QLabel()
        self.label.setPixmap(self.im)
        self.grid = QGridLayout()
        self.grid.addWidget(self.label, 1, 1)
        self.setLayout(self.grid)

        # set window meta info
        self.setGeometry(600, 150, 1, 1)
        self.setWindowTitle("Knot Analysis")
        self.show()

        # begin frame-by-frame refresh timer
        timer = QTimer(self, timeout=self.doTick, interval=1000/tickFPS)
        timer.start()

    # boilderplate for a frame update
    def doTick(self):
        self.kh.computeTick() # figure out what to do
        self.kh.performTick() # do it
        self.update() # re-run paintEvent()

    # boilerplate to handle frame-by-frame updates
    def paintEvent(self, event):
        self.im = QPixmap(self.fileName) # reset background
        self.label.setPixmap(self.im)
        qp = QPainter() # start painting
        qp.begin(self.im)
        qp.setRenderHint(QPainter.Antialiasing, True)
        qp.setRenderHint(QPainter.SmoothPixmapTransform, True)
        self.draw(qp)
        qp.end()
        self.label.setPixmap(self.im) # update image with painting on top

    # paint the stuff each tick
    def draw(self, qp):
        self.kh.draw(qp) # draw stuff


def main():
    app = QApplication(sys.argv)
    ex = KnotCanvas('knot.png', 10)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()