# -*- coding: utf-8 -*-
"""
Created on Sun Aug 30 18:18:56 2015

@author: larry
"""
import os
from PySide import QtCore, QtGui
from common import Common, widgetWithMenu
from editor import Editor

class AbcHighlighter(QtGui.QSyntaxHighlighter):
    """
This method of highlighting current line in red was flawed. To get this to
work, I would need to force redraw of old and new current line. For now,
I'm sticking with just highlighting the current line namber (see editor.py).    
    """
    def highlightBlock(self, text):
        lineNumber = self.currentBlock().blockNumber()
        print (self.parent(), lineNumber, Common.blockNumber, text)
        if lineNumber == Common.blockNumber:
            self.setFormat(0, len(text), QtCore.Qt.red)
"""
// C code snippet for reference if I re-open this battle!
    QTextCharFormat myClassFormat;
     myClassFormat.setFontWeight(QFont.Bold);
     myClassFormat.setForeground(Qt.darkMagenta);
     QString pattern = "\\bMy[A-Za-z]+\\b";

     QRegExp expression(pattern);
     int index = text.indexOf(expression);
     while (index >= 0) {
         int length = expression.matchedLength();
         setFormat(index, length, myClassFormat);
         index = text.indexOf(expression, index + length);
 """
 
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
        
        # disabled (see comments in 'AbcHighlighter' above)
        # self.abcHighlighter = AbcHighlighter(self.document())
    
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
        blockNumber = tc.blockNumber()
        Common.blockNumber = blockNumber
        col = tc.positionInBlock()
        print ('AbcEditor.handleCursorMove: row =', blockNumber,
                                           'col =', col)
        if Common.score:
            Common.score.showAtRowAndCol(blockNumber, col)

    def moveToRowCol(self, row=0, col=0):
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

    def countDown(self, force=None):
        if force:
            self.counted = force
        if self.counted==0:
            return
        self.counted -=1
        #(print 'countDown', self.counted)
        if self.counted:
            return
        print ("autoSave")
        self.saveFile(fileName='./autosaved.abc')

    def newFile(self, fileName='new.abc'):
        self.clear()
        self.setFileName(fileName)

    def loadAnyFile(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self,
                                                         "Choose a data file",
                                                         '', '*.abc')[0]
        print ("loadAnyFile 2", fileName)
        self.loadFile(fileName)

    def loadFile(self, fileName, row=0, col=0):
        print ("AbcEditor.loadFile", fileName)
        f = QtCore.QFile(fileName)

        if f.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            self.readAll(f)
            f.close()
            print ("Loaded %s" % fileName)
            self.setFileName(fileName)
            self.moveToRowCol(row, col)  # primarily to gain focus!

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
        if not Common.abc2abc:
            return
        semitones, ok = QtGui.QInputDialog.getInteger(self,
                "Transpose (automatic clef change(s))",
                "semitones (+/- for up/down:)", 0, -24, 24, 1)
        if not ok:
            return
        fileName = 'original.abc'
        self.originalText = self.toPlainText()
        self.setFileName(fileName)
        self.saveFile(fileName=fileName)
        transposedText = Common.abc2abc.process(fileName,
                                                transpose=semitones)
        self.newFile('transposed.abc')
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

    def saveFileAs(self, fileName=None):
        """
        save the current panel contents to a new file.
        """
        if fileName is None:
            files = QtGui.QFileDialog.getSaveFileName(self,
                *self.saveFileArgs)
            if not files:
                return
            fileName = files[0]
        self.setFileName(fileName)
        self.saveFile()
 
