#!/usr/bin/env python
from __future__ import print_function
"""
Copyright 2015 Hippos Technical Systems BV.
(but borrows somme code from the painting/svgviewer example of PyQt v4.x)
DECLARED OBSOLESCENT per 4th April 2016; see PitchView.py
@author: larry
"""

import sys, re
import numpy as np
from PIL import Image
from ..share import (Share, dbg_print, QtCore, QtGui, image_dir, QtSvg, WithMenu, Printer)
import pyqtgraph as pg
from .terpsichore import default_voice, Clef, Note


# class MyScene(pg.GraphicsScene):
# etc... removed; not working; not necesary?


class FreqView(pg.GraphicsView, WithMenu):
    menuTag = '&Tuning'
    pps = 1000  # points per semitone
    n_samples = 1000

    def menuItems(self):
        return [
        ]

    def __init__(self):
        dbg_print ("FreqView.__init__")
        pg.GraphicsWindow.__init__(self)
        WithMenu.__init__(self)
        # self.setScene(MyScene(self)) # see above

        # avoid showing "window in the making"' during startup.
        # not sure when or why window gets shown again but it does so conveniently!\
        self.hide()
        self.plotStaves()
        self.data = np.array([np.NaN]*self.n_samples, dtype=np.float32)
        self.curve = self.staves_plot.plot(self.data, axisItems={}) # , connect='finite')
        dbg_print ("!FreqView.__init__")

    def plotStaves(self):
        self.staves_plot = self.addPlot()
        self.staves_plot.hideAxis('left')
        self.staves_plot.setYRange(36*self.pps, 80*self.pps)
        #self.staves_plot.setXRange(-self.n_samples, 0)
        self.staves_plot.setXRange(0, self.n_samples)

        all_staff_lines = []  # accumulator
        for clef in (Clef.Bass, Clef.Treble):
            all_staff_lines += clef.lines
            img = Image.open(image_dir + clef.symbol).resize(
                (32*clef.scaleHint, 920*clef.scaleHint), Image.ANTIALIAS)
            img_ar = np.array(img)
            #print(img_ar.shape)
            img_ar_v = np.swapaxes(np.flipud(img_ar.view(dtype=np.uint32).reshape(img_ar.shape[:-1])), 0, 1)
            img_item = pg.ImageItem(img_ar_v, opacity=0.5)
            self.staves_plot.addItem(img_item, autoLevels=False)

            marked_semi = clef.lines[clef.marked]
            img_item.setPos(0, (marked_semi.GetPitch() - clef.descent)*self.pps)

        for ixPitch in range(128):
            note = default_voice.GetNote(ixPitch)
            width = 1
            style = None
            label = note.real_name
            labelOpts={'color': (200,0,0), 'movable': False, 'position': 0.8,
                       'anchors': (0.5, 0.5), 'fill': (0, 0, 200, 100)}
            if note in all_staff_lines:
                colour = (200, 200, 200)
                width = 2
            #elif note is Note.A4: # traditional tuning note nominally 440Hz but often inflated
            #    colour = (0, 200, 0)
            #elif note.pitch == 0:
            elif note is Note.C4:
                label += " = middle C"
                style = QtCore.Qt.DashLine
                colour = (220, 220, 220)
            elif len(note.real_name) == 2:
                colour = (200, 30, 30)
            else:
                colour = (150, 30, 30)
            inf_line = pg.InfiniteLine(movable=False, angle=0, pos=ixPitch*self.pps,
                                       pen=dict(color=colour, width=width, style=style),
                                       # bounds = [-20, 20],
                                       hoverPen=(0,240,0),
                                       label=label, labelOpts=labelOpts)
            self.staves_plot.addItem(inf_line)

    def add_sample(self, volume, freq):
        self.data[:-1] = self.data[1:]
        self.data[-1] = freq is None and np.NaN or (freq * self.pps)
        self.curve.setData(self.data)  # , connect='finite')

    def wheelEvent(self, event):
        factor = 1.2**( event.delta() / 120.0)
        self.scale(factor, factor)
        # self.mustApplyTransform = self.transform()
        dbg_print ("Score.wheelEvent, delta = ", event.delta())
        event.accept()
