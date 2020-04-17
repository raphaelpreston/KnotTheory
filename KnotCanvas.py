# The heart of the operation: displays and runs everything

import sys
import os
import numpy as np
from math import sin, cos, radians
from random import randint
from LineFinder import *
from KnotHandler import *
from skimage import io, color, morphology, img_as_float
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QGridLayout, QWidget
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont, QPen, QImage
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
        self.kh = KnotHandler(self.imageData, self.skelImageData, self.swapImage())

        # boilerplate to add image background from imageData
        height, width, _ = self.imageData.shape
        bytesPerLine = 4 * width
        # arr2 = np.require(self.imageData, np.uint8, 'C')
        # self.normalQImage = QImage(arr2, width, height, QImage.Format_RGB888)
        self.imageData = np.array(self.imageData).reshape(609,583, -1).astype(np.int32)
        self.normalQImage = QImage(self.imageData, self.imageData.shape[0], self.imageData.shape[1], QImage.Format_RGB32)
        # img = PrintImage(QPixmap(qimage))
        # self.normalQImage = QImage(arr2, width, height, bytesPerLine, QImage.Format_RGB888)
        # self.skelQImage = QPixmap(QImage(self.skelImageData, width, height, bytesPerLine, QImage.Format_RGB888))
        self.label = QLabel()
        self.label.setPixmap(QPixmap(self.normalQImage))
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
        pass

    # boilderplate for a frame update
    def doTick(self):
        self.kh.computeTick() # figure out what to do
        self.kh.performTick() # do it
        self.update() # re-run paintEvent()

    # boilerplate to handle frame-by-frame updates
    def paintEvent(self, event):
        pass
        # self.im = QPixmap(self.fileName) # reset background
        # self.label.setPixmap(self.im)
        # qp = QPainter() # start painting
        # qp.begin(self.im)
        # qp.setRenderHint(QPainter.Antialiasing, True)
        # qp.setRenderHint(QPainter.SmoothPixmapTransform, True)
        # self.draw(qp)
        # qp.end()
        # self.label.setPixmap(self.im) # update image with painting on top

    # paint the stuff each tick
    def draw(self, qp):
        self.kh.draw(qp) # draw stuff

def main(): # ignore already declared error
    app = QApplication(sys.argv)
    ex = KnotCanvas('knot.png', 1)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()