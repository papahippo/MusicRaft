#!/usr/bin/env python
# -*- encoding: utf8 -*-
from __future__ import print_function
"""
Copyright 2015 Hippos Technical Systems BV.
(but borrows somme code from the painting/svgviewer example of PyQt v4.x)

@author: larry
"""

import sys, os, re

from ..share import (Share, dbg_print, QtCore, QtGui, QtWebKit, WithMenu, Printer)
from mplayer.core import Player

try:
    _Container =QtGui.QX11EmbedContainer
except ImportError:
    _Container = QtGui


class PlayerView(_Container, WithMenu):

    def __init__(self):
        dbg_print ("PlayerView.__init__")
        _Container.__init__(self)
        WithMenu.__init__(self)
        self.resize(640, 480)
    def showAtRowAndCol(self, row, colhtml_bytes):
        pass  # for now!

    def locateXY(self, x, y):
        pass  # for now!

    #def printAll(self, toPDF=False):
    # .. pending!
