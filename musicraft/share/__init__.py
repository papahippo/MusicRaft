from __future__ import print_function
import sys, os

dbg_print = (os.getenv('ABCRAFT_DBG') and print) or (lambda *pp, **kw: None)

class Share:
    pass

image_path = os.path.normpath(os.path.split(__file__)[0]+'/..') + '/images/'
print('image_path =', image_path)

abcraft_qt = os.getenv('ABCRAFT_QT', 'PySide')
if abcraft_qt == 'PySide':
    from PySide import (QtCore, QtGui, QtSvg, QtWebKit)
    Signal = QtCore.Signal
    dbg_print ("using PySide!")
elif abcraft_qt == 'PyQt4':
    from PyQt4 import (QtCore, QtGui, QtSvg, QtWebKit)
    Signal = QtCore.pyqtSignal
    dbg_print ("using Pyqt4!")
else:
    raise NameError("bad value: ABCRAFT_QT = " + abcraft_qt)


class Printer(QtGui.QPrinter):
    pageSize = QtGui.QPrinter.A4

    def __init__(self):
        dbg_print ("Printer.__init__")
        QtGui.QPrinter.__init__(self, QtGui.QPrinter.HighResolution)
        self.setPageSize(self.pageSize)
        dbg_print ("!Printer.__init__")


class WithMenu(object):
    menuTag = None

    def __init__(self):
        self.menu = QtGui.QMenu(self.menuTag)
        if not (self.menuTag and self.menuItems()):
            return
        for tag, shortcut, func in self.menuItems():
            action = self.myQAction(tag, shortcut=shortcut, triggered=func)
            self.menu.addAction(action)
        Share.raft.menuBar().addMenu(self.menu)

    def menuItems(self):
        return [
        ]

    def myQAction(self, menuText, shortcut=None, triggered=None, enabled=None,
                  checkable=None, checked=None):
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

