#!/usr/bin/env python
# -*- encoding: utf8 -*-
from __future__ import print_function
"""
Copyright 2015 Hippos Technical Systems BV.
(but borrows somme code from the painting/svgviewer example of PyQt v4.x)

@author: larry
"""

import sys, os, re
import lxml.etree
import numpy as np

from ..share import (Share, dbg_print, QtCore, QtGui, QtWebKit, WithMenu, Printer)


class PlayView(QtGui.QWidget, WithMenu):

    def __init__(self):
        dbg_print ("PlayView.__init__")
        QtGui.QWidget.__init__(self)
        WithMenu.__init__(self)

    #def showOutput(self, html_bytes):
    # .. pending!

    def showAtRowAndCol(self, row, colhtml_bytes):
        pass  # for now!

    def locateXY(self, x, y):
        pass  # for now!

    #def printAll(self, toPDF=False):
    # .. pending!
