#!/usr/bin/python
import sys, os, re, subprocess

# import sip
#sip.setapi('QString', 2)
#sip.setapi('QVariant', 2)

from PyQt4 import QtCore, QtGui
from editor import Editor
from abc_svg_view import AbcSvgView


class Common:  # yes, shades of FORTRAN; sorry!
    timer = None
    stdBook = None
    abcm2ps = None
    abcm2svg = None
    abc2midi = None
    abc2abc = None
    printer = None
    abcEditor = None


def myQAction(menuText, parent, shortcut=None, triggered=None, enabled=None, checkable=None, checked=None):
    """ Factory function to emulate older version of QAction.
    """
    action = QtGui.QAction(menuText, parent)
    if shortcut:
        action.setShortcut(shortcut)
    if triggered:
        action.triggered.connect(triggered)
    if enabled is not None:
        action.setEnabled(enabled)
    if checkable is not None:
        action.setCheckable(checkable)
    if checked is not None:
        action.setChecked(checked)
    return action


class ExternalCommand(object):

    cmd = None
    extIn  = '.in'
    extOut = '.out'
    exe = None
    outFileName = None
    
    FileToRead = QtCore.pyqtSignal(str)
    
    def __init__(self):
        print ("ExternalCommand __init__", self.extIn, self.extOut)
        if Common.stdBook is None:
            print ("what? no Common.stdBook")
            self.stdTab = None
        else:
            self.stdTab = StdTab()
        #         inst = Class(self,  stdout=OutBySignal(captureWidget.outputSignal))
            Common.stdBook.widget.addTab(self.stdTab,
                                         self.__class__.__name__)

    def process(self, inFileName):
        print ("ExternalCommand", self.cmd, "run on", inFileName)
        if not inFileName.endswith(self.extIn):
            raise TypeError, ("%s cannot handle this filetype: %s" %
                             (self.__class__.__name__,     inFileName))
        baseName = inFileName[:-len(self.extIn)]
        self.outFileName = baseName+self.extOut
        if self.cmd is not None:
            cmd1 = self.cmd(inFileName, self.outFileName)
            print (cmd1)
            output = subprocess.check_output(cmd1, shell=True, stderr=subprocess.STDOUT)
            self.postProcess(output)

    def postProcess(self, output):
        if self.stdTab is None:
            print "self.stdTab is None!"
            print output
        else:
            self.stdTab.setPlainText(output)
                
class Abcm2ps(ExternalCommand):
    
    extIn  = '.abc'
    extOut = '.ps'
    exe = 'abcm2ps'
    #exe = '/home/larry/musicprogs/abcm2ps-6.4.1/abcm2ps'

    def cmd(self, inF, outF):
        return ('%s -O %s %s'
            %(self.exe, outF, inF) )


class Abcm2svg(ExternalCommand):
    
    extIn  = '.abc'
    extOut = '_page_.svg'
    exe = 'abcm2ps'

    def __init__(self):
        ExternalCommand.__init__(self)
        self.outFile_CRE = re.compile("Output written on\s+(\S.*)\s\(.*")

    def cmd(self, inF, outF):
        return ('%s -v -A -O %s %s'
            %(self.exe, outF, inF) )

    def postProcess(self, output):
        ExternalCommand.postProcess(self, output)
        svgList = []
        for line in output.split('\n'):
            match = self.outFile_CRE.match(line)
            if match:
                svgList.append(match.group(1))
        print (svgList)
        if svgList and Common.abcSvgView:
            Common.abcSvgView.useFiles(svgList)
            Common.abcSvgView.showWhichPage(0)


class Abc2Midi(ExternalCommand):

    extIn  = '.abc'
    extOut = '.midi'
    exe = 'abc2midi'
    
    def cmd(self, inF, outF):
        return ('%s %s -o %s'
            %(self.exe, inF, outF) )


class Abc2abc(ExternalCommand):
    
    extIn  = '.abc'
    extOut = '_t.abc'
    exe = 'abc2abc'

    def cmd(self, inF, outF):
        return ('%s %s -OCC -r %s'
            %(self.exe, inF, outF) )

class widgetWithMenu(object):
    loadFileArgs= ("Choose a data file", '', '*.txt')
    saveFileArgs= ("Save file as", '', '*.txt')
    headerText = 'Edit'
    menuTag = '&File'
    modifiers = 'Ctrl+'
    whereDockable   = QtCore.Qt.AllDockWidgetAreas
    waitCondition = None
    latency = 8
    counted =0
    fileName = None
    minimumWidth = None
    minimumHeight = None

    def menuItems(self):
        return [
                    ('L&oad',  'L', self.loadAnyFile,),
                    ('&Reload',  'R', self.reloadFile,),
                    ('&Save',  'S', self.saveFile,),
                    ('Save &As',  'A', self.saveFileAs,),
                    ('&Print', 'P', self.printFile,),
#                    ('Set &Font', 'F', self.changeMyFont,),
        ]
    def __init__(self, parent, provider=None):  # provider being phaed out!
        self._parent = parent
        self.menu = QtGui.QMenu(self.menuTag, parent)

        for tag, letter, func in self.menuItems():
            action = myQAction(tag, parent,
                        shortcut=self.modifiers+letter, triggered=func)
            self.menu.addAction(action)
        parent.menuBar().addMenu(self.menu)
        #QtGui.QMainWindow().menuWidget ().addMenu(self.menu)

    def loadAnyFile(self):
        fileName = str(QtGui.QFileDialog.getOpenFileName(self, *self.loadFileArgs))
        print "loadAnyFile 2", str(fileName)
        self.loadFile(fileName)
        print "loadAnyFile 6",type(self.fileName)

    def reloadFile(self):
        print self, "ReloadFile", str(self.fileName)
        self.loadFile(self.fileName)
        print "loadAnyFile 6",type(self.fileName)

    def saveFileAs(self, fileName=False):
        """
        save the current panel contents to a new file.
        """
        self.fileName = str(QtGui.QFileDialog.getSaveFileName(self, *self.saveFileArgs))
        self.saveFile()

    def saveFile(selfself):
        pass # STUB!

    def printFile(self):
        print ("'printFile' not yet written")

    def changeMyFont(self):
        font, ok = QtGui.QFontDialog.getFont(self.font(),self)
#           font, ok = QtGui.QFontDialog.getFont(QtGui.QFont(self.toPlainText()), self)
        if ok:
            self.setFont(font)
            #self.textCursor().setCharFormat.document().setFont(font.key())
            #self.fontLabel.setFont(font)
         
class EditorWithMenu(widgetWithMenu, Editor):
    
    def __init__(self, parent, provider=None, dock=None):
        widgetWithMenu.__init__(self, parent=parent, provider=provider)
        Editor.__init__(self)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.setFont(font)
        self.setCursorWidth(4)
        self.setWindowTitle('title')
        self.textChanged.connect(self.handleTextChanged)
        self.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
        self.dock = dock
        Common.timer.timeout.connect(self.countDown)
    

    def handleTextChanged(self):
        self.counted = self.latency  # reset the 'countdown until quite'
        # print 'textChanged', self.counted

    def countDown(self):
        if self.counted==0:
            return
        self.counted -=1
        #print 'countDown', self.counted
        if self.counted:
            return
        print "autoSave"
        self.saveFile()

    def loadFile(self, fileName):
        f = QtCore.QFile(fileName)

        if f.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            self.readAll(f)
            f.close()
            print ("Loaded %s"
                        %fileName)
            self.fileName = fileName
            title = "%s - %s" %(self.headerText, self.fileName)
            print title
            if self.dock:
                self.dock.setWindowTitle(title)
            print "loadFile 9", type(self.fileName)
            # self.propagate()
            # self._parent.fitToWindow()

    def readAll(self, f):
        print ('readAll', self, f)
        stream = QtCore.QTextStream(f)
        text = stream.readAll()
        print len(text)
        self.setPlainText(text)

    def saveFile(self):
        fileName = self.fileName
        if fileName is None:
            return
        f = QtCore.QFile(fileName)

        if not f.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text):
            return
        self.writeAll(f)
        f.close()
        print ("Saved %s (type %s)" % (fileName, type(self.fileName)))
        
        if Common.abcm2svg:
            Common.abcm2svg.process(fileName)
        if Common.abc2midi:
            Common.abc2midi.process(fileName)
            
    def writeAll(self, f):
        f.writeData(self.toPlainText())

 

class AbcEditorWithMenu(EditorWithMenu):
    loadFileArgs= ("Load an existing ABC file", '', '*.abc')
    saveFileArgs= ("Save ABC source to file as", '', '*.abc')
    headerText = 'ABC Edit'
    menuTag = '&ABC'
    minimumWidth = 480
    minimumHeight = None
    

    def menuItems(self):
        return ( EditorWithMenu.menuItems(self) +
        [
                    ('&Quote',  "'", self.Quote,),
                    ('&Save',  'S', self.saveFile,),
                    ('Save &As',  'A', self.saveFileAs,),
                    ('&Print', 'P', self.printFile,),
        ])

    def Quote(self):
        tC = self.textCursor()
        c0 = '#' # dummy non-match!
        while c0 not in "ABCDEFG":
            tC.movePosition(tC.Left, tC.KeepAnchor)
            sel = tC.selectedText()
            c0 = sel[0]
        tC.removeSelectedText()
        tC.insertText('"'+ sel +'"')
        

class StdBook(widgetWithMenu,  QtGui.QTabWidget):
    headerText = 'subprocess output'
    whereDockable   = QtCore.Qt.AllDockWidgetAreas
    
    def __init__(self, parent=None,  provider=None,  dock=None):
        QtGui.QTabWidget.__init__(self,  parent=parent)
        widgetWithMenu.__init__(self, parent=parent, provider=provider)


class Dock(QtGui.QDockWidget):
    def __init__(self, parent, widgetClass, visible=True, provider=None):
        QtGui.QDockWidget.__init__(self, widgetClass.headerText, parent)
        self.setAllowedAreas(widgetClass.whereDockable)
        self.widget = widgetClass(parent, provider=provider, dock=self)
        self.setWidget(self.widget)
        self.setVisible(visible)
        self.widget.menu.addAction(self.toggleViewAction())

    
class StdTab(QtGui.QPlainTextEdit):
    pass

class AbcCraft(QtGui.QMainWindow):

    midiPlayerExe = 'timidity'
    interval = 100

    def __init__(self):
        #print sys.path
        QtGui.QMainWindow.__init__(self)

        Common.timer = QtCore.QTimer()
        Common.timer.start(self.interval)
        
        Common.stdBook = Dock(self,  StdBook,  True)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, Common.stdBook)
        Common.stdBook.setMinimumHeight(140)

        Common.abcm2svg = Abcm2svg()
        Common.abc2Midi = Abc2Midi()
       
        Common.printer = QtGui.QPrinter()

        Common.abcEditor = Dock(self, AbcEditorWithMenu, True)
        Common.abcEditor.setMinimumWidth(640)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, Common.abcEditor)

        Common.abcSvgView = AbcSvgView(self)

        self.setCentralWidget(Common.abcSvgView)

        self.createActions()
        self.createMenus()
        self.setWindowTitle("ABC Craft")
        self.resize(1280, 1024)

        for arg in sys.argv[1:]:
            if arg.endswith('.abc'):
                Common.abcEditor.widget.loadFile(arg)
                # self.fitToWindow()
                break

    def zoomIn(self):
        self.scaleImage(1.25)

    def zoomOut(self):
        self.scaleImage(0.8)

    def normalSize(self):
        self.adjustSize()
        self.scaleFactor = 1.0

    def fitToWindow(self):
        fitToWindow = self.fitToWindowAct.isChecked()
        self.scrollArea.setWidgetResizable(fitToWindow)
        if not fitToWindow:
            self.normalSize()
        self.updateActions()


    def adaptMenu(self):
            self.fitToWindowAct.setEnabled(True)
            self.updateActions()
            if not self.fitToWindowAct.isChecked():
                self.img.adjustSize()
            
    def adjustScrollBar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value()
                                + ((factor - 1) * scrollBar.pageStep()/2)))


    def startMidi(self):
        if not self.abcMidiThread.outFileName:
            return
        #os.startfile(self.abcMidiThread.outFileName)
        #os.system("%s %s" %(self.midiPlayerExe, self.abcMidiThread.outFileName))
        subprocess.Popen((self.midiPlayerExe,
                              self.abcMidiThread.outFileName))     
        #self.message = QtGui.AbcMessage(dock)

    def about(self):
        QtGui.QMessageBox.about(self, "About Image Viewer",
                "<p>The <b>Image Viewer</b> example shows how to combine "
                "QLabel and QScrollArea to display an image. QLabel is "
                "typically used for displaying text, but it can also display "
                "an image. QScrollArea provides a scrolling view around "
                "another widget. If the child widget exceeds the size of the "
                "frame, QScrollArea automatically provides scroll bars.</p>"
                "<p>The example demonstrates how QLabel's ability to scale "
                "its contents (QLabel.scaledContents), and QScrollArea's "
                "ability to automatically resize its contents "
                "(QScrollArea.widgetResizable), can be used to implement "
                "zooming and scaling features.</p>"
                "<p>In addition the example shows how to use QPainter to "
                "print an image.</p>")

    def createActions(self):
        self.startMidiAct = myQAction("Start &Midi", self, shortcut="Ctrl+M",
                triggered=self.startMidi)

        self.exitAct = myQAction("E&xit", self, shortcut="Ctrl+Q",
                triggered=self.close)


        self.aboutAct = myQAction("&About", self, triggered=self.about)

        self.aboutQtAct = myQAction("About &Qt", self,
                triggered=QtGui.qApp.aboutQt)

        self.nextPageAct = myQAction("&Next Page", self,
                enabled=True, shortcut="Ctrl+PgDown",
                triggered=Common.abcSvgView.showNextPage)

        self.prevPageAct = myQAction("Pre&v Page", self,
                enabled=True, shortcut="Ctrl+PgUp",
                triggered=Common.abcSvgView.showPreviousPage)

        self.firstPageAct = myQAction("&1st Page", self,
                enabled=True, shortcut="Ctrl+Home",
                triggered=Common.abcSvgView.showWhichPage)

    def createMenus(self):
        self.midiMenu = QtGui.QMenu("&Midi", self)
        self.midiMenu.addAction(self.startMidiAct)

        self.controlMenu = QtGui.QMenu("&Control", self)
        self.controlMenu.addAction(self.exitAct)

        self.viewMenu = QtGui.QMenu("&View", self)
        # self.viewMenu.addAction(self.zoomInAct)
        # self.viewMenu.addAction(self.zoomOutAct)
        # self.viewMenu.addAction(self.normalSizeAct)

        # self.viewMenu.addSeparator()
        # self.viewMenu.addAction(self.fitToWindowAct)

        # self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.firstPageAct)
        self.viewMenu.addAction(self.prevPageAct)
        self.viewMenu.addAction(self.nextPageAct)

        self.helpMenu = QtGui.QMenu("&Help", self)
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

        self.menuBar().addMenu(self.controlMenu)
        self.menuBar().addMenu(self.viewMenu)
        self.menuBar().addMenu(self.midiMenu)
        self.menuBar().addMenu(self.helpMenu)

    def updateActions(self):
        self.zoomInAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.zoomOutAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.normalSizeAct.setEnabled(not self.fitToWindowAct.isChecked())

if __name__ == '__main__':

    # print (QtGui.QImageReader.supportedImageFormats(), sys.argv,)
    app = QtGui.QApplication(sys.argv)
    abcCraft = AbcCraft()
    abcCraft.show()
    try:
        sys.exit(app.exec_())
    except:
        pass
