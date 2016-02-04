#!/usr/bin/python3
"""
Copyright 2016 Hippos Technical Systems BV.

@author: larry
"""
import sys
from .rafteditor import RaftEditor
from ..share import (Signal, dbg_print, QtCore, QtGui, QtSvg, WithMenu)


class StdBook(QtGui.QTabWidget):
    headerText = 'subprocess output'
    whereDockable   = QtCore.Qt.AllDockWidgetAreas

    def __init__(self, raft, dock=None):
        self.raft = raft
        QtGui.QTabWidget.__init__(self)


class Dock(QtGui.QDockWidget):
    def __init__(self, raft, widgetClass, visible=True):
        QtGui.QDockWidget.__init__(self, widgetClass.headerText)
        self.setAllowedAreas(widgetClass.whereDockable)
        self.widget = widgetClass(raft, dock=self)
        self.setWidget(self.widget)
        self.setVisible(visible)


class Raft(QtGui.QMainWindow, WithMenu):
    menuTag = '&File'

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.stdBook = Dock(self, StdBook,  True)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.stdBook)
        self.stdBook.setMinimumHeight(140)
        self.raftEditor = Dock(self, RaftEditor, True)
        self.raftEditor.setMinimumWidth(640)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.raftEditor)
        self.editor = self.raftEditor.widget
        self.createMenus()
        WithMenu.__init__(self, self)


    def start(self):
        self.show()
        self.openThemAll(sys.argv[1:])

    def openThemAll(self, filenames=()): # False means already in place!
        dbg_print('openThemAll', filenames)
        for fn in filenames:
            self.editor.loadFile(fn)

    def about(self):
        QtGui.QMessageBox.about(self, "About 'Raft'",
                "<p>To be updated!.</p>"
                "<p></p>")

    def createMenus(self):
        self.helpMenu = QtGui.QMenu("&Help", self)
        self.aboutAct = self.myQAction("About &Raft", triggered=self.about)
        self.aboutQtAct = self.myQAction("About &Qt", triggered=QtGui.qApp.aboutQt)
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)
        self.helpAction = self.menuBar().addMenu(self.helpMenu)

    def menuItems(self):
        return [
                    ('&New',           'Ctrl+N', self.editor.newFile,),
                    ('&Open',          'Ctrl+O', self.editor.loadAnyFile,),
                    ('&Close',         'Ctrl+C', self.editor.closeFile,),
                    ('Open in new &Instance', 'Ctrl+I', self.editor.cloneAnyFile,),
                    ('&Reload',        'Ctrl+R', self.editor.reloadFile,),
                    ('R&estart',       'Ctrl+E', self.editor.restart,),
                    ('&Save',          'Ctrl+S', self.editor.saveFile,),
                    ('Save &As',       'Ctrl+A', self.editor.saveFileAs,),
                    ('E&xit',          'Ctrl+Q', self.editor.close,),
#                    ('&Transpose',     'Ctrl+T', self.transpose,),
#                    ('&Undo Transpose','Ctrl+U', self.undoTranspose,),
#                    ('Set &Font', 'F', self.changeMyFont,),
        ]


def main():
    app = QtGui.QApplication(sys.argv)
    raft = Raft()
    raft.start()
    try:
        sys.exit(app.exec_())
    except:
        pass

if __name__ == '__main__':
    main()
