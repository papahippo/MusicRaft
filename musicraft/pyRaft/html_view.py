#!/usr/bin/env python
from __future__ import print_function
"""
Copyright 2015 Hippos Technical Systems BV.
(but borrows somme code from the painting/svgviewer example of PyQt v4.x)

@author: larry
"""

import sys, re
import lxml.etree
import numpy as np

from ..share import (Share, dbg_print, QtCore, QtGui, QtWebKit, WithMenu, Printer)

class HtmlView(QtWebKit.QWebView, WithMenu):

    menuTag = '&Score'

    def menuItems(self):
        return [
#                    ('Set &Font', 'F', self.changeMyFont,),
        ]

    def __init__(self):
        dbg_print ("Score.__init__")
        QtWebKit.QWebView.__init__(self)
        WithMenu.__init__(self)

    def showOutput(self, html_bytes):
        self.setContent(html_bytes)

    def showAtRowAndCol(self, row, col):
        pass  # for now!

    def locateXY(self, x, y):
        pass  # for now!
