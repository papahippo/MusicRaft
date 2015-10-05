#!/usr/bin/env python
from __future__ import print_function
"""
Copyright 2015 Hippos Technical Systems BV.
(but borrows somme code from the painting/svgviewer example of PyQt v4.x)

@author: larry
"""

import sys, re
import lxml.etree
import numpy as np

# from PyQt4 import QtCore, QtGui, QtSvg
#from PySide import QtCore, QtGui, QtSvg

from common import (Common, dbg_print, widgetWithMenu,
                    QtCore, QtGui, QtSvg)

def abcHash(type_, row, col):
   return (type_ and row and col) and ((ord(type_)<<24) + (row<<10) + col)

def abcUnhash(hash_):
    return ((hash_ and chr((hash_>>24)&0xff)),  # type
            (hash_ and (hash_>>10)&0x3fff),     # row
            (hash_ and hash_&0x3ff))     # col
    
class MyScene(QtGui.QGraphicsScene):
        
    def mousePressEvent(self, event):
        scP = event.scenePos()
        x = scP.x()
        y = scP.y()
        dbg_print ("MyScene.mousePressEvent",
               #event.pos(), event.scenePos(), event.screenPos()
               'scenePos x,y =', x, y, 'button =', event.button(),
               'scene width =', self.width(), 'scene height =', self.height(),
        )
        if event.button() == 1:
            Common.score.locateXY(x, y)
            event.accept()
        else:
            event.ignore()


class SvgDigest:
    locatableTypes = ('N', None)
    gScaleMultiplier = 1.0 
 
    def __init__(self, filename):
        self.svg_file = QtCore.QFile(filename)
        #self.buildCribList()
        self.quickDic = {}
        self.svg_tree = self.cursorsDad = None
        
    def buildQuickDic(self, row=None, col=None, type_='N'):
        """ extract the all-imortant information from the .svg
            file which enables us to correlate locations within the
            image with locations within the source abc file.
        """
        if type_ not in self.locatableTypes:
            raise TypeError, (
"only types " + self.locatableTypes + " can be autolocated in this version."
             )
        # maybe need to use row numbers starting from 1 everywhere(?)
        hashToMatch = abcHash(type_, row, col)
        dbg_print ('hashToMatch =', hashToMatch and hex(hashToMatch))
        fileName = str(self.svg_file.fileName())
        if self.svg_tree is None:
            # dbg_print("building 'quick dictionary' from '%s'" % fileName)
            # dbg_print('self.eltCursor =', self.eltCursor)
            for i, attr in enumerate(('x', 'y', 'hash_')):
                if i==2:
                    dtype = np.int32
                else:
                    dtype = np.float_
                self.quickDic[attr] = np.array([], dtype=dtype)
            self.svg_tree = lxml.etree.parse(fileName)
            # root = svg_tree.getroot()
        else:
            self.removeCursor()
        eltCursor = lxml.etree.Element('circle', r='7', stroke='red', 
                          fill="none")
        eltCursor.set('stroke-width', '2')            
        self.abcEltAtCursor = self.eltCursor = dad = None
        eltHead = eltAbc = None

        for elt in self.svg_tree.iter():
            # dbg_print (i, elt.tag, type(elt.tag), str(elt.tag))
            if callable(elt.tag):
                continue
            if (elt.tag.endswith('abc')
            and (elt.get('type') in self.locatableTypes)):
                eltAbc = elt # ready to be paired up with a notehead element
                # use any old ABC record to determine parent ('dad').
                # we may need this for scale information even if we haven't
                # yet found a cursor location!
                #
                dad = eltAbc.getparent()
            elif elt.tag.endswith('use'):
                attr, val = elt.items()[-1]
                if (attr.endswith('href') and val.lower() == '#hd'):
                    eltHead = elt # ready to be paired up with an 'abc' element
            else:
                continue
            if eltAbc is None or eltHead is None:
                continue  # haven't got a note-head/abc pair yet.
                
# we've 'paired' a note-head and an ABC note description; hurrah!
            for i,attr in enumerate(('x','y', 'hash_')):
                if i==2:
                    newVal = abcHash(eltAbc.get('type'),
                                     int(eltAbc.get('row')),
                                     int(eltAbc.get('col')))
                    # dbg_print ('newVal =', hex(newVal))
                else:
                    newVal = float(eltHead.get(attr))
                self.quickDic[attr] = np.append(self.quickDic[attr], newVal)
            if (newVal == hashToMatch):
                dbg_print ('at cursor',
                           [(attr, self.quickDic[attr][-1]) 
                            for attr in ('x', 'y')])
                #, note head x,y, cx, cy =',
                #          latest['x'], latest['y'],
                #          latest['cx'], latest['cy'])
                self.abcEltAtCursor = eltAbc
                for coord in ('x', 'y'):
                    eltCursor.set('c'+ coord, str(self.quickDic[coord][-1]))
            # avoid pairing the same notehead or abc note descripton again!
            eltAbc = eltHead = None

        self.cursorsDad = dad
        transform = dad.get('transform')
        dbg_print (dad, transform)
        scale_match = ((dad is not None)
            and re.match('scale\((.*)\)', transform))
        gScale = (scale_match and float(scale_match.group(1))) or 0.75
        dbg_print ("SvgDigest: scale according to svg section =", gScale)
        self.gScale = gScale * self.gScaleMultiplier
        if self.abcEltAtCursor is None:
            dbg_print ("can't find cursor position!")
            #print (hex(hashToMatch),
            #       [hex(self.quickDic['hash_'][i]) for i in range(2)])
        else:
            dad.insert(0, eltCursor)
            # test only: self.cursorsDad.remove(eltCursor)
            outFile = open(fileName, 'w')
            dbg_print ('written', fileName)
            self.svg_tree.write(outFile)
            self.eltCursor = eltCursor
        return self.abcEltAtCursor

    def removeCursor(self):
        if self.eltCursor is not None and self.cursorsDad is not None:
            self.cursorsDad.remove(self.eltCursor)
            self.eltCursor = None

    def rowColAtXY(self, x, y):
        if not self.quickDic:
            self.buildQuickDic()
        x /= self.gScale # fudgge-factor - investigation still pending!
        y /= self.gScale # fudgge-factor - investigation still pending!
        dbg_print('x,y', x, y, [(a, self.quickDic[a][:8])
            for a in self.quickDic.keys()])
        x_dist = x - self.quickDic['x']
        y_dist = y - self.quickDic['y']
        a_dist = x_dist*x_dist + y_dist*y_dist
        # dbg_print('a_dist', a_dist[:8])
        am = np.argmin(a_dist)
        type_, row, col = abcUnhash(self.quickDic['hash_'][am])
        dbg_print(am, row, col, self.quickDic['x'][am],
                                self.quickDic['y'][am], )
        return row, col  # not sure this is the best place for the '-1'!
        
class Score(QtGui.QGraphicsView, widgetWithMenu):
    menuTag = '&Score'

    def menuItems(self):
        return [
                    ("&Reset Zoom",    'Ctrl+R',      self.resetZoom,),
                    ("&First Page",    'Ctrl+1',      self.showWhichPage,),
                    ("&Next Page",     'Ctrl+PgDown', self.showNextPage,),
                    ("Pre&vious Page", 'Ctrl+PgUp',   self.showPreviousPage,),
                    ('Print &Page',    'Ctrl+P',      self.printPage,),
                    ('Print &Score',   'Ctrl+Alt+P',  self.printScore,),
#                    ('Set &Font', 'F', self.changeMyFont,),
        ]

    def __init__(self, parent=None):
        dbg_print ("Score.__init__", parent)
        widgetWithMenu.__init__(self)
        QtGui.QGraphicsView.__init__(self, parent)
        self.svgItem = None
        self.backgroundItem = None
        self.outlineItem = None
        self.image = QtGui.QImage()

        self.setScene(MyScene(self))
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
        self.which = 0  # default to show first generated svg until we know better.
        self.svgDigests = []
        dbg_print ("!Score.__init__", parent)

    def drawBackground(self, p, rect):
        p.save()
        p.resetTransform()
        p.drawTiledPixmap(self.viewport().rect(),
                self.backgroundBrush().texture())
        p.restore()

    def useFiles(self, filenames=()):
        self.svgDigests = [SvgDigest(filename) for filename in filenames]
        for path in filenames:
            svg_file = QtCore.QFile(path)
            if not svg_file.exists():
                QtGui.QMessageBox.critical(self, "Open SVG File",
                        "Could not open file '%s'." % path)
        self.showWhichPage(self.which, force=True)

    def showAtRowAndCol(self, row, col):
        dbg_print ('showAtRowAndCol', row, col)
        l = len(self.svgDigests)        
        for i in range(l):
            j = (i +self.which) % l
            abcEltAtCursor = self.svgDigests[j].buildQuickDic(row, col)
            if abcEltAtCursor is not None:
                break
        else:
            dbg_print ("can't find svg graphics correspond to row : col...",
                   row, ':', col)
            return
        self.showWhichPage(j, force=True)

    def locateXY(self, x, y):
        row, col = self.svgDigests[self.which].rowColAtXY(x, y)
        dbg_print ("locateXY(", x, y, " > row,co", row, col)
        if Common.abcEditor:
            Common.abcEditor.widget.moveToRowCol(row, col)

    def showNextPage(self):
        dbg_print ('showNextPage')
        return self.showWhichPage(self.which + 1)

    def showPreviousPage(self):
        dbg_print ('showPreviousPage')
        return self.showWhichPage(self.which - 1)

    def showWhichPage(self, which=0, force=False):
        dbg_print ('----- showWhichPage', which)
        which %= len(self.svgDigests)
        if (not force) and (which==self.which):
            return
        svg_file = self.svgDigests[which].svg_file
        if not svg_file.exists():
            raise IOError, ("'%s' does not exist!" % svg_file.filename())
        self.which = which
        s = self.scene()

        s.clear()

        self.svgItem = QtSvg.QGraphicsSvgItem(svg_file.fileName())
        self.svgItem.setFlags(QtGui.QGraphicsItem.ItemClipsToShape)
        self.svgItem.setCacheMode(QtGui.QGraphicsItem.NoCache)
        self.svgItem.setZValue(0)

        self.backgroundItem = QtGui.QGraphicsRectItem(self.svgItem.boundingRect())
        self.backgroundItem.setBrush(QtCore.Qt.white)
        self.backgroundItem.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        self.backgroundItem.setVisible(True)
        self.backgroundItem.setZValue(-1)

        self.outlineItem = QtGui.QGraphicsRectItem(self.svgItem.boundingRect())
        outline = QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.DashLine)
        outline.setCosmetic(True)
        self.outlineItem.setPen(outline)
        self.outlineItem.setBrush(QtGui.QBrush(QtCore.Qt.NoBrush))
        self.outlineItem.setVisible(True)
        self.outlineItem.setZValue(1)

        s.addItem(self.backgroundItem)
        s.addItem(self.svgItem)
        s.addItem(self.outlineItem)

        rect = self.outlineItem.boundingRect()
        # dbg_print (rect)
        s.setSceneRect(rect) # .adjusted(-10, -10, 10, 10))

        self.setViewport(QtGui.QWidget())

        self.backgroundItem.setVisible(True)
        self.outlineItem.setVisible(False)

    def resetZoom(self):
        self.resetTransform()

    def printPage(self, *whichPages):
        if not whichPages:
            whichPages = self.which,
        if not QtGui.QPrintDialog(Common.printer, self).exec_():
            return
        painter = QtGui.QPainter(Common.printer)
        thatPage = self.which
        for j in whichPages:
            self.showWhichPage(j)
            self.scene().render(painter)
        self.showWhichPage(thatPage)

    def printScore(self):
        self.printPage(self, *range(len(self.svgDigests)))

    def wheelEvent(self, event):
        factor = 1.2**( event.delta() / 120.0)
        self.scale(factor, factor)
        # self.mustApplyTransform = self.transform()
        dbg_print ("Score.wheelEvent, delta = ", event.delta())
        event.accept()


if __name__ == '__main__':

    class MainWindow(QtGui.QMainWindow):
        def __init__(self):
            super(MainWindow, self).__init__()
    
            self.currentPath = ''
    
            self.score = Score()
    
            fileMenu = QtGui.QMenu("&File", self)
            quitAction = fileMenu.addAction("E&xit")
            quitAction.setShortcut("Ctrl+Q")
    
            self.menuBar().addMenu(fileMenu)
    
    
            quitAction.triggered.connect(QtGui.qApp.quit)
    
            self.setCentralWidget(self.score)
            self.setWindowTitle("SVG Viewer")
            self.view.useFiles(sys.argv[1:] or
                ['./allTunes_page_00%d.svg' % i for i in range(1, 4)  ])
            self.resize(self.view.sizeHint() + QtCore.QSize(
                80, 80 + self.menuBar().height()))


    app = QtGui.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
