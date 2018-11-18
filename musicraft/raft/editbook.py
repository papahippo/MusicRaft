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
    fileLoaded = Signal(QtGui.QPlainTextEdit, str)

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
        #self.setWidth(640)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.countDown)
        self.timer.start(self.interval)
        self.filenamesDropped.connect(self.pickUpFiles)
        self.currentChanged.connect(self.activateCurrent)
        #self.fileLoaded.connect(self.fixTabName)

    #def fixTabName(self, fileName):
    #    pass

    def countDown(self, force=None):
        if force:
            self.counted = force
        if self.counted==0:
            return
        self.counted -=1
        # dbg_print('countDown', self.counted)
        if not self.counted:
            self.activeEdit.handleLull()

    def newFile(self):
        self.openThemAll(force=True)

    def setActiveEdit(self, ed):
        self.activeEdit = ed
        self.setCurrentWidget(ed)
        ed.editBecomesActive.emit()



    def activateCurrent(self, ix):
        dbg_print('activateCurrent', ix)
        self.activeEdit = self.editors[ix]
        # quick fix below needs to be improved!
        if not self.activeEdit.fileName:
            return
        self.activeEdit.setFileName() # to force chdir!
        self.activeEdit.handleLull(force=True)
        # self.activeEdit.editBecomesActive.emit()

    # temporary hacks while getting tabbed approach working:

    def transpose(self):
        self.activeEdit.transpose()

    def openThemAll(self, *filenames, force=False):
        for fn in filenames:
            ed = Editor(book=self)
            self.editors.append(ed)
            self.addTab(ed, os.path.split(fn)[1])
            ed.loadFile(fn)
            self.setActiveEdit(ed)

    def pickUpFiles(self, fnList):
        return self.openThemAll(*fnList)

    def reloadFile(self):
        self.activeEdit.reloadFile()

    def saveFile(self):
        self.activeEdit.saveFile()

    def saveFileAs(self):
        self.activeEdit.saveFileAs()

    def closeFile(self):
        self.activeEdit.closeFile()
        self.editors.remove(self.activeEdit)
        self.removeTab(self.currentIndex())
        self.openThemAll()

    def restart(self):
        self.activeEdit.restart()

    def moveToRowCol(self, *location):
        self.activeEdit.moveToRowCol(*location)

    def exit_etc(self):
        while True:
            unsaved = [(editor.specialSaveFileName is not None) for editor in self.editors]
            print ('unsaved', unsaved)
            n_unsaved = sum(unsaved)
            if not n_unsaved:
                break
            ret = QtGui.QMessageBox.warning(self, "Application",
                ("There are unsaved changes in %u document(s).\n" % n_unsaved) +
                "Do you want to save your changes?",
                QtGui.QMessageBox.SaveAll | QtGui.QMessageBox.Discard |
                        QtGui.QMessageBox.Cancel)
            if ret == QtGui.QMessageBox.Cancel:
                return False
            if ret == QtGui.QMessageBox.Discard:
                break
            for editor in self.editors:
                if editor.specialSaveFileName is None:
                    continue
                editor.saveFile()
        sys.exit()
