#!/usr/bin/python3
"""
Copyright 2016 Hippos Technical Systems BV.

@author: larry
"""
import sys
from .editbook import EditBook
from ..share import (Share, Signal, dbg_print, QtCore, QtGui, QtSvg, WithMenu)
from .external import (StdOut, StdErr)
#import qdarkstyle

class StdBook(QtGui.QTabWidget):
    headerText = 'error/diagnostic output'
    whereDockable   = QtCore.Qt.AllDockWidgetAreas

    def __init__(self, dock=None):
        QtGui.QTabWidget.__init__(self)

class DisplayBook(QtGui.QTabWidget):
    pass  # for now
class Dock(QtGui.QDockWidget):
    def __init__(self, widgetClass, visible=True):
        QtGui.QDockWidget.__init__(self, widgetClass.headerText)
        self.setAllowedAreas(widgetClass.whereDockable)
        self.widget = widgetClass(dock=self)
        self.setWidget(self.widget)
        self.setVisible(visible)


class Raft(QtGui.QMainWindow, WithMenu):
    menuTag = '&File'

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Share.raft = self
        self.resize(1280, 1024)
        self.stdBook = Dock(StdBook,  True)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.stdBook)
        self.stdBook.setMinimumHeight(140)
        self.raftEditor = Dock(EditBook, True)
        # self.raftEditor.setMinimumWidth(320)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.raftEditor)
        self.editor = self.raftEditor.widget
        sys.stdout = StdOut()
        sys.stderr = StdErr()
        print ("testing stdout...", file=sys.stdout)
        print ("testing stderr...", file=sys.stderr)
        #sys.exit(0)
        self.createMenus()
        self.displayBook = DisplayBook()
        self.setCentralWidget(self.displayBook)
        #self.displayBook.setBaseSize(640, 480)
        #self.displayBook.addTab(QtGui.QGraphicsView(), "test widget")
        WithMenu.__init__(self)


    def start(self):
        self.show()
        self.editor.openThemAll(sys.argv[1:])

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
                    #('Open in new &Instance', 'Ctrl+I', self.editor.cloneAnyFile,),
                    ('&Reload',        'Ctrl+R', self.editor.reloadFile,),
                    ('R&estart',       'Ctrl+E', self.editor.restart,),
                    ('&Save',          'Ctrl+S', self.editor.saveFile,),
                    ('Save &As',       'Ctrl+A', self.editor.saveFileAs,),
                    ('E&xit',          'Ctrl+Q', self.exit_etc),
                    ('&Transpose',     'Ctrl+T', self.editor.transpose,),
#                    ('Set &Font', 'F', self.changeMyFont,),
        ]
    def exit_etc(self):
        # quick fix;to be reviewed!
        sys.exit()

def main(Plugins=()):
    app = QtGui.QApplication(sys.argv)
    # app.setStyleSheet(qdarkstyle.load_stylesheet())
    Raft()
    Share.plugins = []
    for Plugin in Plugins:
        try:
            Share.plugins.append(Plugin())
        except TypeError as exc:
            print(exc, file=sys.stderr)

    Share.raft.start()
    try:
        sys.exit(app.exec_())
    except:
        pass

if __name__ == '__main__':
    main()
