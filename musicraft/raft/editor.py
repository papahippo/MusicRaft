#!/usr/bin/python
#partially based on: http://john.nachtimwald.com/2009/08/15/qtextedit-with-line-numbers/ (MIT license)
from __future__ import print_function
import sys, os, subprocess
from ..share import (Share, Signal, dbg_print, QtCore, QtGui, QtSvg, temp_dir)

##LMY: from highlighter import PythonHighlighter

class Editor(QtGui.QPlainTextEdit):

    headerText = 'Edit'
    prevCursorPos = -1
    currentLineColor = None
    editBecomesActive = Signal()

    def __init__(self, book=None, **kw):
        self.book = book
        QtGui.QPlainTextEdit.__init__(self, **kw)
        self.lineNumberArea = self.LineNumberArea(self)
        self.viewport().installEventFilter(self)
        
        self.newDocument = True
        self.path = ''
        css = '''
        QPlainTextEdit {
          font-family: monospace;
          font-size: 10;
          color: black;
          background-color: white;
          selection-color: white;
          selection-background-color: #437DCD;
        }'''
        self.setStyleSheet(css)

        font = self.font()
        font.setPointSize(10)
        self.setFont(font)
        self.setCursorWidth(2)
        self.setWindowTitle('title')
        self.textChanged.connect(self.handleTextChanged)
        self.editBecomesActive.connect(self.handleTextChanged)
        self.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
        self.cursorPositionChanged.connect(self.handleCursorMove)
        self.originalText = None
        self.haveLoadedFile = False

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
        self.book.counted = self.book.latency
        return

    def moveToRowCol(self, row=1, col=0):
        block = self.document().findBlockByLineNumber (row-1)
        desiredPosition = block.position() + col
        dbg_print ('AbcEditor.moveToRowCol', row, col,
               'desiredPosition', desiredPosition)
        tc = self.textCursor()
        tc.setPosition(desiredPosition)
        self.setTextCursor(tc)
        self.setFocus()

    def highlight(self, tc):
        blockNumber = tc.blockNumber()
        # Common.blockNumber = blockNumber
        col0 =  col = tc.positionInBlock()
        l = tc.block().length()
        dbg_print ("autoTrack", l)
        blockText = tc.block().text()
        while col and ((col >= (l-1))
            or not (str(blockText[col]).lower() in 'abcdefg')):
            col -= 1
        dbg_print ('editor.highlight: row =', blockNumber,
                                           'col =', col, col0)
        #if Common.score:
        #    Common.score.showAtRowAndCol(blockNumber+1, col)
        self.book.settledAt.emit(blockNumber+1, col)
        hi_selection = QtGui.QTextEdit.ExtraSelection()

        hi_selection.format.setBackground(self.palette().alternateBase())
        hi_selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection,
                                        True)
        if self.currentLineColor is not None:
            hi_selection.format.setBackground(self.currentLineColor)
        #setFontUnderline(True)
        hi_selection.cursor = tc
        self.setExtraSelections([hi_selection])
        hi_selection.cursor.clearSelection()


    def handleTextChanged(self):
        self.book.counted = self.book.latency
        dbg_print ('handleTextChanged', self.book.counted)

    def handleLull(self):
        if 1:  # self.document().isModified():
            dbg_print ("autoSave")
            split = os.path.split(self.fileName)
            fileName = 'autosave_'.join(split)
            self.saveFile(
                fileName=temp_dir+ '/autosave_' + os.path.split(self.fileName)[1])
        tc = self.textCursor()
        position = tc.position()
        if position != self.prevCursorPos:
            self.prevCursorPos = position
            self.highlight(tc)

    def newFile(self, fileName='new.abc'):
        self.clear()
        self.setFileName(fileName)
        self.book.fileLoaded.emit(fileName)

    def closeFile(self):
        self.clear()
        self.haveLoadedFile = False

    def cloneAnyFile(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self,
                                                         "Choose a data file",
                                                         '', '*.abc')[0]
        dbg_print ("cloneAnyFile 2", fileName)
        self.loadFile(fileName, newInstance=True)

    def restart(self):
        self.loadFile(self.fileName)
        sys.exit(0)

    def loadFile(self, fileName, newInstance=None, row=1, col=0):
        dbg_print ("AbcEditor.loadFile", fileName, newInstance, row, col)
        if newInstance is None:
            newInstance = False # self.haveLoadedFile
        if newInstance:
            dbg_print("need to create new instance for", fileName)
            sys.argv[1:] = fileName,
            subprocess.Popen(sys.argv)
            return

        self.setFileName(fileName)
        f = QtCore.QFile(fileName)

        if not f.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            return

        self.readAll(f)
        f.close()
        dbg_print ("Loaded %s" % fileName)
        self.moveToRowCol(row, col)  # primarily to gain focus!
        self.document().setModified(True) # force rewrite of Score
        self.book.fileLoaded.emit(fileName)

    def setFileName(self, fileName=None):
        if fileName is not None:
            self.fileName = fileName
        title = "%s - %s" % (self.headerText, os.path.abspath(self.fileName))
        dbg_print (title)
        # self.book.dock.setWindowTitle(title)
        self.haveLoadedFile = True

    def readAll(self, f):
        dbg_print ('readAll', self, f)
        stream = QtCore.QTextStream(f)
        text = stream.readAll()
        self.setPlainText(text)

    def saveFile(self, fileName=None,):
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
        dbg_print ("Saved %s " % fileName)
        self.document().setModified(False)
        self.book.fileSaved.emit(fileName)
        return

    def transpose(self):
        semitones, ok = QtGui.QInputDialog.getInteger(self,
                "Transpose (automatic clef change(s))",
                "semitones (+/- for up/down:)", 0, -24, 24, 1)
        if not ok:
            return
        newFileName, ok  = QtGui.QFileDialog.getSaveFileName(self, "write tansposed to file",
                            "transposed.abc",
                            "(*.abc)")
        if not ok:
            return
        transposedText = Share.abcRaft.abc2abc.process(self.fileName,
                                                transpose=semitones)
        with open(newFileName, 'w') as transposed_file:
            transposed_file.write(transposedText)
        self.book.openThemAll((newFileName,))

    def writeAll(self, out):
        text = self.toPlainText()
        # dbg_print('len(text)=', len(text))
        out.write(text)

    def reloadFile(self):
        dbg_print ("ReloadFile", self.fileName)
        self.loadFile(self.fileName)

    def saveFileAs(self, fileName=None, show=True):
        """
        save the current panel contents to a new file.
        """
        if fileName is None:
            files = QtGui.QFileDialog.getSaveFileName(self,
                "Save source to file as", '', '*.abc')
            if not files:
                return
            fileName = files[0]
        if show:
            self.setFileName(fileName)
        self.saveFile()
        self.book.setTabText(self.book.currentIndex(), os.path.split(fileName)[1])

    def resizeEvent(self,e):
        self.lineNumberArea.setFixedHeight(self.height())
        QtGui.QPlainTextEdit.resizeEvent(self,e)

    def eventFilter(self, object, event):
        if object is self.viewport():
            self.lineNumberArea.update()
            return False
        return QtGui.QPlainTextEdit.eventFilter(object, event)

    def keyPressEvent(self, event):
        """Reimplement Qt method"""
        key = event.key()
        # print (type(event))
        meta = event.modifiers() & QtCore.Qt.MetaModifier
        ctrl = event.modifiers() & QtCore.Qt.ControlModifier
        shift = event.modifiers() & QtCore.Qt.ShiftModifier
        plain = not (meta or ctrl or shift)
        if key == QtCore.Qt.Key_Insert and plain:
            self.setOverwriteMode(not self.overwriteMode())
        if key == QtCore.Qt.Key_Tab and plain and self.snippets:
            return self.autoComplete(event)
        else:
            QtGui.QPlainTextEdit.keyPressEvent(self, event)

    def autoComplete(self, event):
        print ('autoComplete')
        tc = self.textCursor()
        col0 =  col = tc.positionInBlock()
        block = tc.block()
        l = block.length()
        print ("autoComplete", l)
        blockText = block.text()
        while col and ((col >= (l-1))
            or not (str(blockText[col-1]) in ' |!')):
            tc.deletePreviousChar()
            col -= 1
        key = blockText[col:col0]
        print ("autoComplete key %d:%d '%s'" % (col, col0, key))
        snippet = self.snippets.get(key, ("!%s!" % key,))
        
        # rough and ready starter implementation:
        for i, piece in enumerate(snippet):
            tc.insertText(piece)
            if i==0:
                pos = tc.position()
        tc.setPosition(pos)
        self.setTextCursor(tc) 

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
            self.book.filenamesDropped.emit(paths)
        elif source.hasText():
            print ("dropEvent", "hasText")
            #editor = self.get_current_editor()
            #if editor is not None:
            #    editor.insert_text( source.text() )
        event.acceptProposedAction()

    def mousePressEvent(self, mouseEvent):
        if (mouseEvent.button() in (QtCore.Qt.LeftButton, QtCore.Qt.RightButton)):
            QtGui.QPlainTextEdit.mousePressEvent(self, mouseEvent)
        print (mouseEvent.button() )
        return

    snippets = {
        'V': ('V:', ' name="', '" sname="', '"\n',),  # new voice
        'Q': ('Q:1/4',),  # new tempo indication
        '12': ('[1 ', ' :| [2 ',),  # varied repeat ending coding
        'cr': ('!<! ', ' !<!)',),  # hairpin dynamic
        'dim': ('!>! ', ' !>!)',),  # hairpin dynamic
        'CR': ('"_cresc."',),
        'Cr': ('"^cresc."',),
        'MR': ('"_molto rit."',),
        'Mr': ('"^molto rit."',),
        'PR': ('"_poco rit."',),
        'Pr': ('"^poco rit."',),
        'SB': ('"_steady beat"',),
        'Sb': ('"^steady beat"',),
        'm': ('[M:', '2/', '4]',),  # mid-line time-sig change
        'tt': ('!tenuto!',),
        'tp': ('!teepee!',),
        'ac': ('!>!',),  # accent; '><TAB>' also works
        'ro': ('!///!',),  # roll/roffel; '///<TAB>' also works
        'st': ('!dot!',),  # staccato; 'dot<TAB>' also works
        '.': ('!dot!',),  # staccato; 'dot<TAB>' also works
        'gl': ('!-(!', '!-)!'),  # glissando
    }

    class LineNumberArea(QtGui.QWidget):

        def __init__(self, editor):
            QtGui.QWidget.__init__(self, editor)
            self.edit = editor
            self.highest_line = 0
            css = '''
            QWidget {
              font-family: monospace;
              font-size: 10;
              color: black;
            }'''
            self.setStyleSheet(css)
 
        def update(self, *args):
            width = QtGui.QFontMetrics(
                self.edit.document().defaultFont()).width(
                    str(self.highest_line)) + 10
            if self.width() != width:
                self.setFixedWidth(width)
                self.edit.setViewportMargins(width,0,0,0)
            QtGui.QWidget.update(self, *args)
 
        def paintEvent(self, event):
            page_bottom = self.edit.viewport().height()
            font_metrics = QtGui.QFontMetrics(
                self.edit.document().defaultFont())
            current_block = self.edit.document().findBlock(
                self.edit.textCursor().position())
 
            painter = QtGui.QPainter(self)
            painter.fillRect(self.rect(), QtCore.Qt.lightGray)
            
            block = self.edit.firstVisibleBlock()
            viewport_offset = self.edit.contentOffset()
            line_count = block.blockNumber()
            painter.setFont(self.edit.document().defaultFont())
            while block.isValid():
                line_count += 1
                # The top left position of the block in the document
                position = self.edit.blockBoundingGeometry(block).topLeft() + viewport_offset
                # Check if the position of the block is out side of the visible area
                if position.y() > page_bottom:
                    break
 
                # We want the line number for the selected line to be bold.
                bold = False
                x = self.width() - font_metrics.width(str(line_count)) - 3
                y = round(position.y()) + font_metrics.ascent()+font_metrics.descent()-1
                if block == current_block:
                    bold = True
                    font = painter.font()
                    font.setBold(True)
                    painter.setFont(font)
                    pen = painter.pen()
                    painter.setPen(QtCore.Qt.red)
                    painter.drawRect(0, y-14, self.width()-2, 20)
                    painter.setPen(pen)
                    
                # Draw the line number right justified at the y position of the
                # line. 3 is a magic padding number. drawText(x, y, text).
                painter.drawText(x, y, str(line_count))
 
                # Remove the bold style if it was set previously.
                if bold:
                    font = painter.font()
                    font.setBold(False)
                    painter.setFont(font)
 
                block = block.next()
 
            self.highest_line = line_count
            painter.end()
 
            QtGui.QWidget.paintEvent(self, event)
