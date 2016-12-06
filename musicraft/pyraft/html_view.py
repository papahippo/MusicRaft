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


class HtmlView(QtWebKit.QWebView, WithMenu):

    menuTag = '&Html'

    def menuItems(self):
        return [
                    ('&Print',         None,  self.printAll,),
                    ('E&xport to PDF', None,  self.printAllToPDF,),
        ]

    def __init__(self):
        dbg_print ("HtmlView.__init__")
        QtWebKit.QWebView.__init__(self)
        WithMenu.__init__(self)

    def showOutput(self, html_bytes):
        self.setHtml(html_bytes)
        with open(self.fileName, 'w') as output:
            output.write(html_bytes)

    def showAtRowAndCol(self, row, colhtml_bytes):
        pass  # for now!

    def locateXY(self, x, y):
        pass  # for now!

    def printAll(self, toPDF=False):
        dbg_print("printAll!")
        self.printer.setPageSize(QtGui.QPrinter.A4)
        self.printer.setOutputFormat(QtGui.QPrinter.PdfFormat)
        #self.printer.setOutputFileName(toPDF and self.compositeName or '')
        # see quick fix in .external! ...
        printName = toPDF and (os.path.splitext(self.fileName)[0] + '.pdf') or ''
        printName = printName.replace('autosave_', '')
        dbg_print("printing to file ", printName)
        self.printer.setOutputFileName(printName)
        self.print_(self.printer)
