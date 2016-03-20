#!/usr/bin/env python
from __future__ import print_function
"""
Copyright 2015 Hippos Technical Systems BV.
(but borrows somme code from the painting/svgviewer example of PyQt v4.x)

@author: larry
"""

import sys, re
import numpy as np

from ..share import (Share, dbg_print, QtCore, QtGui, QtSvg, WithMenu, Printer)
import pyqtgraph as pg
print(pg.__file__)
class MyScene(QtGui.QGraphicsScene):
        
    def _mousePressEvent(self, event):
        scP = event.scenePos()
        x = scP.x()
        y = scP.y()
        dbg_print ("MyScene.mousePressEvent",
               #event.pos(), event.scenePos(), event.screenPos()
               'scenePos x,y =', x, y, 'button =', event.button(),
               'scene width =', self.width(), 'scene height =', self.height(),
        )
        if event.button() == 1:
            self.parent().locateXY(x, y)
            event.accept()
        else:
            event.ignore()


#class FreqView(QtGui.QGraphicsView, WithMenu):
class FreqView(pg.GraphicsWindow):
    menuTag = '&Tuning'

    def menuItems(self):
        return [
        ]

    def __init__(self):
        dbg_print ("FreqView.__init__")
        #QtGui.QGraphicsView.__init__(self)
        pg.GraphicsWindow.__init__(self)
        # WithMenu.__init__(self)
        # self.setScene(MyScene(self))
        # self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        # self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
        self.resize(1000,600)
        self.plotStaves()
        dbg_print ("!FreqView.__init__")

    def plotStaves(self):
        self.staves_plot = self.addPlot()
        self.staves_plot.setYRange(60, 88)
        for ixPitch in range(128):
            inf_line = pg.InfiniteLine(movable=True, angle=0, pos=ixPitch,
                                       pen=(0, 0, 200), # bounds = [-20, 20],
                                       hoverPen=(0,200,0), label=str(ixPitch),
                       labelOpts={'color': (200,0,0), 'movable': True, 'fill': (0, 0, 200, 100)})
            self.staves_plot.addItem(inf_line)

    def wheelEvent(self, event):
        factor = 1.2**( event.delta() / 120.0)
        self.scale(factor, factor)
        # self.mustApplyTransform = self.transform()
        dbg_print ("Score.wheelEvent, delta = ", event.delta())
        event.accept()
