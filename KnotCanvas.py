import sys
from math import sin, cos, radians
from random import randint
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QFont, QPen
from PyQt5.QtCore import Qt, QTimer

class KnotCanvas(QWidget):

	def __init__(self):
		super().__init__()
		# class variables
		self.arrowPosition = (200, 200)
		self.arrowSize = 150
		self.arrowAngle = 180

		# init everything else
		self.initUI()
		
		# begin refresh timer
		timer = QTimer(self, timeout=self.getArrowPosition, interval=1000)
		timer.start()
		
	def initUI(self):      
		self.setGeometry(600, 200, 400, 400)
		self.setWindowTitle('Knot Analysis')
		self.show()

	def getArrowPosition(self):
		self.arrowPosition = (randint(0, 400), randint(0, 400))
		self.arrowSize = randint(2, 100)
		self.arrowAngle = randint(0,360)
		print('Arrow of size {} pointing at ({}, {}) with angle {}...'.format(
			self.arrowSize,
			self.arrowPosition[0],
			self.arrowPosition[1],
			self.arrowAngle
		))
		self.update() # run paintEvent()

	def paintEvent(self, event):
		qp = QPainter()
		qp.begin(self)
		qp.setRenderHint(QPainter.Antialiasing, True)
		qp.setRenderHint(QPainter.SmoothPixmapTransform, True)
		self.drawArrow(
			qp,
			self.arrowPosition[0],
			self.arrowPosition[1],
			self.arrowSize,
			self.arrowAngle
		)
		qp.end()

	def drawArrow(self, qp, x, y, size, deg):
		# convert to radians and get opposite angle to be more intuitive
		rad = radians((deg+180) % 360)

		# get initial endpoints of body and tips
		pivotX = x
		pivotY = y
		bodyX = pivotX + size
		bodyY = pivotY
		tip1X = pivotX + size/3
		tip1Y = pivotY + size/6
		tip2X = pivotX + size/3
		tip2Y = pivotY - size/6

		# rotate endpoints around the pivot
		eBodyX = (bodyX-pivotX) * cos(rad) - (bodyY-pivotY) * sin(rad) + pivotX
		eBodyY = (bodyX-pivotX) * sin(rad) + (bodyY-pivotY) * cos(rad) + pivotY
		eTip1X = (tip1X-pivotX) * cos(rad) - (tip1Y-pivotY) * sin(rad) + pivotX
		eTip1Y = (tip1X-pivotX) * sin(rad) + (tip1Y-pivotY) * cos(rad) + pivotY
		eTip2X = (tip2X-pivotX) * cos(rad) - (tip2Y-pivotY) * sin(rad) + pivotX
		eTip2Y = (tip2X-pivotX) * sin(rad) + (tip2Y-pivotY) * cos(rad) + pivotY

		# draw the arrow
		pen = QPen(Qt.red, 2, Qt.SolidLine)
		qp.setPen(pen)

		# body
		qp.drawLine(pivotX, pivotY, eBodyX, eBodyY) 

		# tips
		qp.drawLine(pivotX, pivotY, eTip1X, eTip1Y)
		qp.drawLine(pivotX, pivotY, eTip2X, eTip2Y)

if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = KnotCanvas()
	sys.exit(app.exec_())
