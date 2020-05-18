# The heart of the operation: displays and runs everything

import sys
import os
from math import sin, cos, radians
from random import randint
from LineFinder import *
from KnotHandler import *
from skimage import io, color, morphology, img_as_float, img_as_uint
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QGridLayout, QWidget
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont, QPen
from PyQt5.QtCore import Qt, QTimer

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

class KnotCanvas(QWidget):

    def __init__(self, givenFilePath, tickFPS):
        super().__init__()

        # extract file directory and path
        lastSlash = givenFilePath.rindex("/")
        fileName = givenFilePath[lastSlash+1:]
        knotsPath = givenFilePath[:lastSlash]
        
        self.skelFilePath = "{}/skeletons/skeleton_{}.png".format(knotsPath, fileName)
        self.filePath = "{}/{}".format(knotsPath, fileName)

        # skeletonize image
        image = img_as_float(color.rgb2gray(io.imread(self.filePath)))
        image_binary = image < 0.5
        self.skelImageData = morphology.skeletonize(image_binary)
        io.imsave(self.skelFilePath, img_as_uint(self.skelImageData)) # TODO: delete when done

        # declare class variables
        self.imageData = io.imread(self.filePath) # get image data with sci-kit
        self.kh = KnotHandler(self.imageData, self.skelImageData, self.swapImage)

        # add image background
        self.normalPixmap = QPixmap(self.filePath)
        self.skelPixmap = QPixmap(self.skelFilePath)
        self.activeImg = 'normal'
        self.label = QLabel()
        self.label.setPixmap(self.normalPixmap)
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

    # swaps image displaying from normal to skeleton
    def swapImage(self):
        if self.activeImg == 'normal':
            self.label.setPixmap(self.skelPixmap)
            self.activeImg = 'skel'
        else:
            self.label.setPixmap(self.normalPixmap) # todo: break this up into 2 function
            self.activeImg = 'normal'

    # boilderplate for a frame update
    def doTick(self):
        self.kh.computeTick() # figure out what to do
        self.kh.performTick() # do it
        self.update() # re-run paintEvent()

    # boilerplate to handle frame-by-frame updates
    def paintEvent(self, event):
        self.normalPixmap = QPixmap(self.filePath)
        self.skelPixmap = QPixmap(self.skelFilePath)
        self.label.setPixmap(self.normalPixmap if self.activeImg == 'normal' else self.skelPixmap)

        qp = QPainter() # start painting
        qp.begin(self.normalPixmap if self.activeImg == 'normal' else self.skelPixmap)
        qp.setRenderHint(QPainter.Antialiasing, True)
        qp.setRenderHint(QPainter.SmoothPixmapTransform, True)
        self.draw(qp)
        qp.end()
        self.label.setPixmap(self.normalPixmap if self.activeImg == 'normal' else self.skelPixmap) # update image with painting on top

    # paint the stuff each tick
    def draw(self, qp):
        self.kh.draw(qp) # draw stuff

def main(): # ignore already declared error
    app = QApplication(sys.argv)
    ex = KnotCanvas('knots/medium_testing.png', 10000)
    sys.exit(app.exec_())

    # TODO: add some functionality to tell if the endpoitn finding has failed (maybe original arc thickness)
    # TODO: fix multiple spines

if __name__ == '__main__':
    main()