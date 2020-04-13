# libarary for drawing stuff given a QPainter object

from math import sin, cos, radians

def drawArrow(qp, x, y, size, degreeRot):
    # convert to radians and get opposite angle to be more intuitive
    rad = radians((degreeRot+180) % 360)

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

    # body
    qp.drawLine(pivotX, pivotY, eBodyX, eBodyY) 

    # tips
    qp.drawLine(pivotX, pivotY, eTip1X, eTip1Y)
    qp.drawLine(pivotX, pivotY, eTip2X, eTip2Y)