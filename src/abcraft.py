#!/usr/bin/python
from __future__ import print_function
import sys, os, re, subprocess
from PySide import QtCore, QtGui
from abceditor import AbcEditor
from score import Score
from common import Common, myQAction, widgetWithMenu


class ExternalCommand(object):

    cmd = None
    extIn  = '.in'
    extOut = '.out'
    exe = None
    outFileName = None
    errOnOut = False
    FileToRead = QtCore.Signal(str)
    
    def __init__(self):
        print ("ExternalCommand __init__", self.extIn, self.extOut)
        if Common.stdBook is None:
            print ("what? no Common.stdBook")
            self.stdTab = None
        else:
            self.stdTab = StdTab()
            Common.stdBook.widget.addTab(self.stdTab,
                                         self.__class__.__name__)

    def process(self, inFileName, **kw):
        print ("ExternalCommand", self.cmd, kw, "run on", inFileName)
        if not inFileName.endswith(self.extIn):
            raise TypeError, ("%s cannot handle this filetype: %s" %
                             (self.__class__.__name__,     inFileName))
        baseName = inFileName[:-len(self.extIn)]
        self.outFileName = baseName+self.extOut
        if self.cmd is not None:
            cmd1 = self.cmd(inFileName, self.outFileName, **kw)
            print (cmd1)
            if self.errOnOut:
                stderr = subprocess.STDOUT
            else:
                stderr = subprocess.PIPE
            process = subprocess.Popen(cmd1, stdout=subprocess.PIPE,
                                             stderr=stderr,
                                             shell=True)
            output, error = process.communicate()
            _retcode = process.poll()
            if _retcode:
                pass
            #    raise subprocess.CalledProcessError(retcode,
            #                                        cmd1, output=output)
            
            if self.errOnOut:
                self.postProcess(output)
                return None
            else:
                self.postProcess(error)
                return output

    def postProcess(self, error):
        if self.stdTab is None:
            print ("self.stdTab is None!")
        else:
            self.stdTab.setPlainText(error)
                
class Abcm2ps(ExternalCommand):
    
    extIn  = '.abc'
    extOut = '.ps'
    exe = 'abcm2ps'
    #exe = '/home/larry/musicprogs/abcm2ps-6.4.1/abcm2ps'

    def cmd(self, inF, outF, **kw):
        return ('%s -O %s %s'
            %(self.exe, outF, inF) )


class Abcm2svg(ExternalCommand):
    
    extIn  = '.abc'
    extOut = '_page_.svg'
    exe = '/usr/local/bin/abcm2ps'

    def __init__(self):
        ExternalCommand.__init__(self)
        self.outFile_CRE = re.compile("Output written on\s+(\S.*)\s\(.*")

    def cmd(self, inF, outF, **kw):
        return ('%s -v -A -O %s %s'
            %(self.exe, outF, inF) )

    def postProcess(self, error):
        ExternalCommand.postProcess(self, error)
        svgList = []
        for line in error.split('\n'):
            match = self.outFile_CRE.match(line)
            if match:
                svgList.append(match.group(1))
        print (svgList)
        if svgList and Common.score:
            Common.score.useFiles(svgList)
            # Common.score.showWhichPage(0)


class Abc2midi(ExternalCommand):

    extIn  = '.abc'
    extOut = '.midi'
    exe = '/usr/local/bin/abc2midi'
    errOnOut = True
    
    def cmd(self, inF, outF, **kw):
        return ('%s %s -EA -o %s'
            %(self.exe, inF, outF) )


class Abc2abc(ExternalCommand):
    
    extIn  = '.abc'
    extOut = '_t.abc'
    exe = '/usr/local/bin/abc2abc'

    def cmd(self, inF, outF, transpose=None, **kw):
        flags = ''
        if transpose is not None:
            flags += '-t %d' % transpose
        return ('%s %s -OCC -r %s'
            %(self.exe, inF, flags) )


class StdBook(widgetWithMenu,  QtGui.QTabWidget):
    headerText = 'subprocess output'
    whereDockable   = QtCore.Qt.AllDockWidgetAreas
    
    def __init__(self, dock=None):
        QtGui.QTabWidget.__init__(self)
        widgetWithMenu.__init__(self)


class Dock(QtGui.QDockWidget):
    def __init__(self, widgetClass, visible=True):
        QtGui.QDockWidget.__init__(self, widgetClass.headerText)
        self.setAllowedAreas(widgetClass.whereDockable)
        self.widget = widgetClass(dock=self)
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
        Common.abcraft = self
        Common.timer = QtCore.QTimer()
        Common.timer.start(self.interval)
        
        self.createActions()
        self.createMenus()

        Common.stdBook = Dock(StdBook,  True)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, Common.stdBook)
        Common.stdBook.setMinimumHeight(140)

        Common.abcm2svg = Abcm2svg()
        Common.abc2midi = Abc2midi()
        Common.abc2abc = Abc2abc()
        Common.score = Score(self)

        self.setCentralWidget(Common.score)
       
        Common.printer = QtGui.QPrinter(QtGui.QPrinter.HighResolution)
        Common.printer.setPageSize(QtGui.QPrinter.A4)

        Common.abcEditor = Dock(AbcEditor, True)
        Common.abcEditor.setMinimumWidth(640)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, Common.abcEditor)
        self.setWindowTitle("ABCraft")
        self.resize(1280, 1024)

        for arg in sys.argv[1:]:
            if arg.endswith('.abc'):
                Common.abcEditor.widget.loadFile(arg)
                break

    def startMidi(self):
        if not self.abcMidiThread.outFileName:
            return
        subprocess.Popen((self.midiPlayerExe,
                              self.abcMidiThread.outFileName))     
        #self.message = QtGui.AbcMessage(dock)

    def about(self):
        QtGui.QMessageBox.about(self, "About abcaft",
                "<p>To be updated!.</p>"
                "<p></p>")

    def createActions(self):
        self.startMidiAct = myQAction("Start &Midi",shortcut="Ctrl+M",
                triggered=self.startMidi)

        self.exitAct = myQAction("E&xit", shortcut="Ctrl+Q",
                                 triggered=self.close)


        self.aboutAct = myQAction("About AB&Craft", triggered=self.about)

        self.aboutQtAct = myQAction("About &Qt", triggered=QtGui.qApp.aboutQt)

    def createMenus(self):
        self.controlMenu = QtGui.QMenu("AB&Craft", self)
        self.controlMenu.addAction(self.exitAct)

        self.midiMenu = QtGui.QMenu("&Midi", self)
        self.midiMenu.addAction(self.startMidiAct)

        self.helpMenu = QtGui.QMenu("&Help", self)
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

        self.menuBar().addMenu(self.controlMenu)
        self.menuBar().addMenu(self.midiMenu)
        self.menuBar().addMenu(self.helpMenu)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    abcCraft = AbcCraft()
    abcCraft.show()
    try:
        sys.exit(app.exec_())
    except:
        pass
