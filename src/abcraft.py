#!/usr/bin/python
from __future__ import print_function
import sys, os, re, subprocess
from PySide import QtCore, QtGui
from abceditor import AbcEditor
from score import Score
from common import Common, myQAction, widgetWithMenu
from external import Abc2midi, Abcm2svg, Abc2abc 


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


def main():
    app = QtGui.QApplication(sys.argv)
    abcCraft = AbcCraft()
    abcCraft.show()
    try:
        sys.exit(app.exec_())
    except:
        pass

if __name__ == '__main__':
    main()
