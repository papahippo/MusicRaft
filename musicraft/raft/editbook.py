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
    minimumHeight = None # 800

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
            self.activeEdit.handleLull()

    def newFile(self, fileName='new.abc', force=True):
        if (not force) and self.editors:
            return
        self.clear()
        self.setFileName(fileName)

    def openThemAll(self, filenames=()):
        if (not filenames):
            return self.newFile(force=False)
        dbg_print('openThemAll', filenames)
        for fn in filenames:
            ed = Editor(book=self)
            self.editors.append(ed)
            self.addTab(ed, os.path.split(fn)[1])
            ed.loadFile(fn)
        self.setActiveEdit(ed)

    def loadAnyFile(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self,
                                                         "Choose a data file",
                                                         '.', '*.*')[0]
#                                                         '.', '*.abc')[0]
        dbg_print ("loadAnyFile 2", fileName)
        self.openThemAll((fileName,))

# temporary hacks while getting tabbed approach working:

    def reloadFile(self):
        self.activeEdit.reloadFile()

    def saveFile(self):
        self.activeEdit.saveFile()

    def saveFileAs(self):
        self.activeEdit.saveFileAs()

    def closeFile(self):
        self.activeEdit.closeFile()

    def restart(self):
        self.activeEdit.restart()

    def moveToRowCol(self, *location):
        self.activeEdit.moveToRowCol(*location)

