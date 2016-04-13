# -*- coding: utf-8 -*-
"""
Copyright 2015 Hippos Technical Systems BV.
Created on Sun Aug 30 18:18:56 2015

@author: larry
"""
import sys, os, subprocess
from ..share import (Signal, dbg_print, QtCore, QtGui, QtSvg, temp_dir)
from .editor import Editor


class EditBook(QtGui.QTabWidget):
    minimumWidth = 480
    minimumHeight = None
    interval = 100
    latency = 3
    editors = []
    filenamesDropped = Signal(list)
    settledAt = Signal(int, int)
    fileSaved = Signal(str)
    fileLoaded = Signal(str)

# hastily rescued from widgetWithMenu mix-in:
#
    menuTag = '&File'
    whereDockable   = QtCore.Qt.AllDockWidgetAreas
    waitCondition = None
    latency = 8
    counted =0
    fileName = None
    minimumWidth = 640
    minimumHeight = 800

    headerText = 'Edit'

    def __init__(self, dock=None):
        dbg_print ("EditBook.__init__", dock)
        self.dock = dock
        QtGui.QTabWidget.__init__(self)
        if self.minimumHeight:
            self.setMinimumHeight(self.minimumHeight)
        if self.minimumWidth:
            self.setMinimumWidth(self.minimumWidth)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.countDown)
        self.timer.start(self.interval)
        self.filenamesDropped.connect(self.openThemAll)

    def countDown(self, force=None):
        if force:
            self.counted = force
        if self.counted==0:
            return
        self.counted -=1
#        (dbg_print 'countDown', self.counted)
        if self.counted:
            self.editors[-1].handleLull()

    def newFile(self, fileName='new.abc'):
        self.clear()
        self.setFileName(fileName)

    def openThemAll(self, filenames=()): # False means already in place!
        dbg_print('openThemAll', filenames)
        for fn in filenames:
            ed = Editor(book=self)
            self.editors.append(ed)
            self.addTab(ed, os.path.split(fn)[1])
            ed.loadFile(fn)

    def loadAnyFile(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self,
                                                         "Choose a data file",
                                                         '.', '*.*')[0]
#                                                         '.', '*.abc')[0]
        dbg_print ("loadAnyFile 2", fileName)
        self.loadFile(fileName, newInstance=False)

# temporary hacks while getting tabbed approach working:

    def reloadFile(self):
        self.editors[-1].reloadFile()

    def saveFile(self):
        self.editors[-1].saveFile()

    def saveFileAs(self):
        self.editors[-1].saveFileAs()

    def closeFile(self):
        self.editors[-1].closeFile()

    def restart(self):
        self.editors[-1].restart()

    def moveToRowCol(self, *location):
        self.editors[-1].moveToRowCol(*location)
