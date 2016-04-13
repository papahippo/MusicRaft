# -*- coding: utf-8 -*-
"""
Copyright 2015 Hippos Technical Systems BV.
Created on Sun Aug 30 18:18:56 2015

@author: larry
"""
import sys, os, subprocess
from ..share import (Share, Signal, dbg_print, QtCore, QtGui, QtSvg, temp_dir)
from .editor import Editor


class RaftEditor(Editor):
    minimumWidth = 480
    minimumHeight = None
    interval = 100
    latency = 3
    prevCursorPos = -1 
    currentLineColor = None

    filenamesDropped = Signal(list)

# hastily rescued from widgetWithMenu mix-in:
#
    headerText = 'Edit'
    menuTag = '&File'
    whereDockable   = QtCore.Qt.AllDockWidgetAreas
    waitCondition = None
    latency = 8
    counted =0
    fileName = None
    minimumWidth = None
    minimumHeight = None


    def __init__(self, dock=None):
        dbg_print ("AbcEditor.__init__", dock)
        Editor.__init__(self)
        self.timer = QtCore.QTimer()
        self.timer.start(self.interval)
        font = self.font()
        font.setPointSize(10)
        self.setFont(font)
        self.setCursorWidth(2)
        self.setWindowTitle('title')
        self.textChanged.connect(self.handleTextChanged)
        self.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
        self.dock = dock
        self.timer.timeout.connect(self.countDown)
        self.cursorPositionChanged.connect(self.handleCursorMove)
        self.filenamesDropped.connect(self.openThemAll)
        self.originalText = None
        self.haveLoadedFile = False
        self.setMinimumHeight(400)

    def newFile(self, fileName='new.abc'):
        self.clear()
        self.setFileName(fileName)

    def openThemAll(self, filenames=()): # False means already in place!
        dbg_print('openThemAll', filenames)
        for fn in filenames:
            self.loadFile(fn)

    def loadAnyFile(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self,
                                                         "Choose a data file",
                                                         '.', '*.*')[0]
#                                                         '.', '*.abc')[0]
        dbg_print ("loadAnyFile 2", fileName)
        self.loadFile(fileName, newInstance=False)

    def loadFile(self, fileName, newInstance=None, row=1, col=0):
        dbg_print ("AbcEditor.loadFile", fileName, newInstance, row, col)
        if newInstance is None:
            newInstance = self.haveLoadedFile
        if newInstance:
            dbg_print("need to create new instance for", fileName)
            sys.argv[1:] = fileName,
            subprocess.Popen(sys.argv)
            return

        f = QtCore.QFile(fileName)

        if not f.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            return

        self.readAll(f)
        f.close()
        dbg_print ("Loaded %s" % fileName)
        self.setFileName(fileName)
        self.moveToRowCol(row, col)  # primarily to gain focus!
        self.document().setModified(True) # force rewrite of Score
        self.fileLoaded.emit(fileName)

    #------ Drag and drop
    def dragEnterEvent(self, event):
        """Reimplement Qt method
        Inform Qt about the types of data that the widget accepts"""
        source = event.mimeData()
        if source.hasUrls():
            
            if 1: #mimedata2url(source, extlist=EDIT_EXT):
                print ("dragEnterEvent", "hasUrls")
                event.acceptProposedAction()
            else:
                event.ignore()
        elif source.hasText():
            print ("dragEnterEvent", "hasText")
            event.acceptProposedAction()
        else:
            event.ignore()
            
    def dropEvent(self, event):
        """Reimplement Qt method
        Unpack dropped data and handle it"""
        source = event.mimeData()
        if source.hasUrls():
            #paths = map(filenameFromUrl, source.urls())
            paths = [url.path() for url in source.urls()]
            print ("dropEvent", "hasUrls", source.urls(), paths)
            self.filenamesDropped.emit(paths)
        elif source.hasText():
            print ("dropEvent", "hasText")
            #editor = self.get_current_editor()
            #if editor is not None:
            #    editor.insert_text( source.text() )
        event.acceptProposedAction()
 
