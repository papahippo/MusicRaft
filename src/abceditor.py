# -*- coding: utf-8 -*-
"""
Created on Sun Aug 30 18:18:56 2015

@author: larry
"""
import os
from PySide import QtCore, QtGui
from common import Common, widgetWithMenu
from editor import Editor

class AbcEditor(widgetWithMenu, Editor):
    loadFileArgs= ("Load an existing ABC file", '', '*.abc')
    saveFileArgs= ("Save ABC source to file as", '', '*.abc')
    headerText = 'ABC Edit'
    menuTag = '&ABC'
    minimumWidth = 480
    minimumHeight = None

    def __init__(self, dock=None):
        widgetWithMenu.__init__(self)
        Editor.__init__(self)
        #font = QtGui.QFont()
        font = self.font()
        font.setPointSize(10)
        self.setFont(font)
        self.setCursorWidth(4)
        self.setWindowTitle('title')
        self.textChanged.connect(self.handleTextChanged)
        self.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
        self.dock = dock
        Common.timer.timeout.connect(self.countDown)
        self.cursorPositionChanged.connect(
            self.handleCursorMove)
        self.originalText = None

    def menuItems(self):
        return [
                    ('&New',           'Ctrl+N', self.newFile,),
                    ('&Open',          'Ctrl+L', self.loadAnyFile,),
                    ('&Reload',        'Ctrl+R', self.reloadFile,),
                    ('&Save',          'Ctrl+S', self.saveFile,),
                    ('Save &As',       'Ctrl+A', self.saveFileAs,),
                    ('&Transpose',     'Ctrl+T', self.transpose,),
                    ('&Undo Transpose','Ctrl+U', self.undoTranspose,),
#                    ('Set &Font', 'F', self.changeMyFont,),
        ]

    def Quote(self):
        tC = self.textCursor()
        c0 = '#' # dummy non-match!
        while c0 not in "ABCDEFG":
            tC.movePosition(tC.Left, tC.KeepAnchor)
            sel = tC.selectedText()
            c0 = sel[0]
        tC.removeSelectedText()
        tC.insertText('"'+ sel +'"')
        
    def handleCursorMove(self):
        tc = self.textCursor()
        row = tc.blockNumber()
        col = tc.positionInBlock()
        print ('AbcEdito.handleCursorMove: row =', row, 'col =', col)
        if Common.score:
            Common.score.showAtRowAndCol(row, col)

    def moveToRowCol(self, row, col):
        block = self.document().findBlockByLineNumber (row)
        desiredPosition = block.position() + col
        print ('AbcEditor.moveToRowCol', row, col,
               'desiredPosition', desiredPosition)
        tc = self.textCursor()
        tc.setPosition(desiredPosition)
        self.setTextCursor(tc)
        self.setFocus()

    def handleTextChanged(self):
        self.counted = self.latency  # reset the 'countdown until quite'
        # print ('textChanged', self.counted)

    def countDown(self):
        if self.counted==0:
            return
        self.counted -=1
        #(print 'countDown', self.counted)
        if self.counted:
            return
        print ("autoSave")
        self.saveFile(fileName='./autosaved.abc')

    def newFile(self):
        self.clear()
        self.setFileName('new.abc')

    def loadAnyFile(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self,
                                                         "Choose a data file",
                                                         '', '*.abc')[0]
        print ("loadAnyFile 2", fileName)
        self.loadFile(fileName)

    def loadFile(self, fileName):
        print ("AbcEditor.loadFile", fileName)
        f = QtCore.QFile(fileName)

        if f.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            self.readAll(f)
            f.close()
            print ("Loaded %s" % fileName)
            self.setFileName(fileName)            

    def setFileName(self, fileName=None):
        if fileName is not None:
            self.fileName = fileName
        title = "%s - %s" % (self.headerText, os.path.abspath(self.fileName))
        print (title)
        if self.dock:
            self.dock.setWindowTitle(title)

    def readAll(self, f):
        print ('readAll', self, f)
        stream = QtCore.QTextStream(f)
        text = stream.readAll()
        self.setPlainText(text)

    def saveFile(self, fileName=None):
        if fileName is None:
            fileName = self.fileName
        if fileName is None:
            return
        #f = QtCore.QFile(fileName)
        out = open(fileName, 'w')
        if not out:
            return
        self.writeAll(out)
        out.close()
        print ("Saved %s " % fileName)
        
        if Common.abcm2svg:
            Common.abcm2svg.process(fileName)
        if Common.abc2midi:
            Common.abc2midi.process(fileName)

    def transpose(self):
        fileName = self.fileName
        if not Common.abc2abc:
            return
        semitones, ok = QtGui.QInputDialog.getInteger(self,
                "Transpose (automatic clef change(s))",
                "semitones (+/- for up/down:)", 0, -24, 24, 1)
        if not ok:
            return

        transposedText = Common.abc2abc.process(fileName,
                                                transpose=semitones)
        self.originalText = self.toPlainText()
        self.setPlainText(transposedText)
        
    def undoTranspose(self):
        if self.originalText:
            self.setPlainText(self.originalText)
            self.originalText = None

    def writeAll(self, out):
        text = self.toPlainText()
        print('len(text)=', len(text))
        out.write(text)

    def reloadFile(self):
        print ("ReloadFile", self.fileName)
        self.loadFile(self.fileName)

    def saveFileAs(self, fileName=False):
        """
        save the current panel contents to a new file.
        """
        files = QtGui.QFileDialog.getSaveFileName(self,
            *self.saveFileArgs)
        if not files:
            return
        self.setFileName(files[0])
        self.saveFile()
 
