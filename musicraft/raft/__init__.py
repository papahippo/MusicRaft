#!/usr/bin/python3
"""
Copyright 2016 Hippos Technical Systems BV.

@author: larry
"""
import sys
from rafteditor import RaftEditor
from share import (Signal, dbg_print, QtCore, QtGui, QtSvg)


class StdBook(QtGui.QTabWidget):
    headerText = 'subprocess output'
    whereDockable   = QtCore.Qt.AllDockWidgetAreas

    def __init__(self, dock=None):
        QtGui.QTabWidget.__init__(self)


class Dock(QtGui.QDockWidget):
    def __init__(self, widgetClass, visible=True):
        QtGui.QDockWidget.__init__(self, widgetClass.headerText)
        self.setAllowedAreas(widgetClass.whereDockable)
        self.widget = widgetClass(dock=self)
        self.setWidget(self.widget)
        self.setVisible(visible)


class Raft(QtGui.QMainWindow):

    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.stdBook = Dock(StdBook,  True)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.stdBook)
        self.stdBook.setMinimumHeight(140)
        self.raftEditor = Dock(RaftEditor, True)
        self.raftEditor.setMinimumWidth(640)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.raftEditor)
        self.editor = self.raftEditor.widget
        self.createMenus()
        self.openThemAll(sys.argv[1:])

    def openThemAll(self, filenames=()): # False means already in place!
        dbg_print('openThemAll', filenames)
        for fn in filenames:
            self.editor.loadFile(fn)

    def about(self):
        QtGui.QMessageBox.about(self, "About 'Raft'",
                "<p>To be updated!.</p>"
                "<p></p>")

    def myQAction(self, menuText, shortcut=None, triggered=None, enabled=None,
                  checkable=None, checked=None):
        """ Factory function to emulate older version of QAction.
        """
        action = QtGui.QAction(menuText, self)
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

    def createMenus(self):

        self.fileMenu = QtGui.QMenu('&File')

        for tag, shortcut, func in self.menuItems():
            action = self.myQAction(tag, shortcut=shortcut, triggered=func)
            self.fileMenu.addAction(action)
        self.menuBar().addMenu(self.fileMenu)

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
    raft.show()
    try:
        sys.exit(app.exec_())
    except:
        pass

if __name__ == '__main__':
    main()
