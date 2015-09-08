#!/usr/bin/python
"""
Copyright 2015 Hippos Technical Systems BV.

@author: larry
"""
from __future__ import print_function
from PySide import QtCore, QtGui

dbg_print = lambda *pp, **kw: None
# replace (or overrule in certain modules) above to show debug printout by...
# dbg_print = print
# ... or use soemething more pythonically correct like the logging module!

class Common:  # yes, shades of FORTRAN; sorry!
    timer = None
    stdBook = None
    abcm2ps = None
    abcm2svg = None
    abc2midi = None
    abc2abc = None
    printer = None
    abcEditor = None
    score = None
    abcraft = None
    snippets = {
        'V': ('V:', ' name="', '" sname="', '"\n',),    # new voice
        'Q': ('Q:1/4', ),                 # new tempo indication
        '12': ('[1 ', ' :| [2 ',),        # varied repeat ending coding
        'cr': ('!<! ', ' !<!)',),         # hairpin dynamic
        'dim': ('!>! ', ' !>!)',),        # hairpin dynamic
        'CR': ('"_cresc."',),
        'Cr': ('"^cresc."',),
        'MR': ('"_molto rit."',),
        'Mr': ('"^molto rit."',),
        'PR': ('"_poco rit."',),
        'Pr': ('"^poco rit."',),
        'SB': ('"_steady beat"',),
        'Sb': ('"^steady beat"',),
        'm': ('[M:', '2/', '4]',),       # mid-line time-sig change 
        'tt': ('!tenuto!',),
        'tp': ('!teepee!',),
        'ac': ('!>!',),                  # accent; '><TAB>' also works
        'ro': ('!///!',),                # roll/roffel; '///<TAB>' also works
        'st': ('!dot!',),                # staccato; 'dot<TAB>' also works
        '.': ('!dot!',),                 # staccato; 'dot<TAB>' also works
        'gl': ('!-(!', '!-)!'),          # glissando
    }
    

def myQAction(menuText, shortcut=None, triggered=None, enabled=None,
              checkable=None, checked=None):
    """ Factory function to emulate older version of QAction.
    """
    action = QtGui.QAction(menuText, Common.abcraft)
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

class widgetWithMenu(object):
    loadFileArgs= ("Choose a data file", '', '*.txt')
    saveFileArgs= ("Save file as", '', '*.txt')
    headerText = 'Edit'
    menuTag = '&File'
    whereDockable   = QtCore.Qt.AllDockWidgetAreas
    waitCondition = None
    latency = 8
    counted =0
    fileName = None
    minimumWidth = None
    minimumHeight = None

    def __init__(self):  # provider being phaed out!
        self.menu = QtGui.QMenu(self.menuTag)
        if not self.menuItems():
            return
        for tag, shortcut, func in self.menuItems():
            action = myQAction(tag, shortcut=shortcut, triggered=func)
            self.menu.addAction(action)
        Common.abcraft.menuBar().addMenu(self.menu)
        #QtGui.QMainWindow().menuWidget ().addMenu(self.menu)

    def menuItems(self):
        return [
        ]
            
    def changeMyFont(self):
        font, ok = QtGui.QFontDialog.getFont(self.font(),self)
#           font, ok = QtGui.QFontDialog.getFont(QtGui.QFont(self.toPlainText()), self)
        if ok:
            self.setFont(font)
            #self.textCursor().setCharFormat.document().setFont(font.key())
            #self.fontLabel.setFont(font)
         
