from __future__ import print_function
import sys, os

dbg_print = (os.getenv('ABCRAFT_DBG') and print) or (lambda *pp, **kw: None)

abcraft_qt = os.getenv('ABCRAFT_QT', 'PySide')
if abcraft_qt == 'PySide':
    from PySide import QtCore, QtGui, QtSvg
    Signal = QtCore.Signal
    dbg_print ("using PySide!")
elif abcraft_qt == 'PyQt4':
    from PyQt4 import QtCore, QtGui, QtSvg
    Signal = QtCore.pyqtSignal
    dbg_print ("using Pyqt4!")
else:
    raise NameError("bad value: ABCRAFT_QT = " + abcraft_qt)
