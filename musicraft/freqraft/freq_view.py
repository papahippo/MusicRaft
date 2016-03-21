#!/usr/bin/env python
from __future__ import print_function
"""
Copyright 2015 Hippos Technical Systems BV.
(but borrows somme code from the painting/svgviewer example of PyQt v4.x)

@author: larry
"""

import sys, re
import numpy as np
from PIL import Image
from ..share import (Share, dbg_print, QtCore, QtGui, QtSvg, WithMenu, Printer)
import pyqtgraph as pg
from .terpsichore import default_voice


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
class FreqView(pg.GraphicsView):
    menuTag = '&Tuning'

    def menuItems(self):
        return [
        ]

    def __init__(self):
        dbg_print ("FreqView.__init__")
        print(dir(self))
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
        self.staves_plot.setYRange(10*16, 50*16)
        self.staves_plot.setXRange(0, 500)
        for ixPitch in range(128):
            inf_line = pg.InfiniteLine(movable=True, angle=0, pos=ixPitch*16,
                                       pen=(0, 0, 200), # bounds = [-20, 20],
                                       hoverPen=(0,200,0),
                                       label=default_voice.GetNote(ixPitch).real_name,
                       labelOpts={'color': (200,0,0), 'movable': True, 'fill': (0, 0, 200, 100)})
            self.staves_plot.addItem(inf_line)
        img = Image.open('/home/larry/python/fortuna440/images/Bass_clef_inv.png')
        img_ar = np.array(img)
        print(img_ar.shape)
        img_ar_v = np.swapaxes(np.flipud(img_ar.view(dtype=np.uint32).reshape(img_ar.shape[:-1])), 0, 1)
        img_item = pg.ImageItem(img_ar_v, opacity=0.5)
        self.staves_plot.addItem(img_item, autoLevels=False)
        img_item.setPos(0, 256)

    def wheelEvent(self, event):
        factor = 1.2**( event.delta() / 120.0)
        self.scale(factor, factor)
        # self.mustApplyTransform = self.transform()
        dbg_print ("Score.wheelEvent, delta = ", event.delta())
        event.accept()
