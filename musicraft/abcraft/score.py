#!/usr/bin/env python3
"""
Copyright 2015 Hippos Technical Systems BV.
(but borrows some code from the painting/svgviewer example of PyQt v4.x)

@author: larry
"""

import sys, re
import lxml.etree
import numpy as np
from collections import OrderedDict
from ..share import (Share, dbg_print, QtCore, QtGui, QtWebKit, WithMenu)


class MyScene(QtGui.QGraphicsScene):
        
    def mousePressEvent(self, event):
        scP = event.scenePos()
        x = scP.x()
        y = scP.y()
        dbg_print ("MyScene.mousePressEvent: "+
               #event.pos(), event.scenePos(), event.screenPos()
               'scenePos x,y =' + str(x) + ',' + str(y), '  button =' + str(event.button()),
               'scene width =' + str(self.width()) + ' scene height ='+ str(self.height()),
                self.parent())
        if event.button() == 1:
            self.parent().locateXY(x, y)
            event.accept()
        else:
            event.ignore()

    def wheelEvent1(self, event):
        modifiers = QtGui.QApplication.keyboardModifiers()
        if not (modifiers & QtCore.Qt.ControlModifier):
            return  QtGui.QGraphicsScene.wheelEvent(self, event)
        factor = 1.2**( event.delta() / 120.0)
        # self.scale(factor, factor)
        # self.mustApplyTransform = self.transform()
        dbg_print ("MyScene.wheelEvent, delta = ", event.delta())
        event.accept()


class SvgDigest:
    ringColour = 'green'

    locatableTypes = ('N', 'R', 'Z')
    scene = None

    def __init__(self, filename):
        self.svg_file = QtCore.QFile(filename)
        self.quickDic = {}
        self.svg_tree = self.cursorsDad = None
        self.row_col_dict = OrderedDict()
        self.buildQuickDic()

    def AdjustForScene(self, scene):
        self.scene = scene

    def buildQuickDic(self):
        """ extract the all-imortant information from the .svg
            file which enables us to correlate locations within the
            image with locations within the source abc file.
            N.B. row/col/cursor related stuff is being gradually phased
            out from this function.
        """
        fileName = str(self.svg_file.fileName())

        for attr, dtype in (('row',   np.int32), ('col',   np.int32),
                            ('x',     np.float), ('y',     np.float),
                            ('scale', np.float )):
            self.quickDic[attr] = np.array([], dtype=dtype)

        self.svg_tree = lxml.etree.parse(fileName)
        self.abcEltAtCursor = self.eltCursor = dad = None
        eltHead = eltAbc = None
        scale_ = 1.0
        for elt in self.svg_tree.iter():
            if callable(elt.tag):
                continue
            tag_ = elt.tag.split('}')[1]  # get rid of pesky namespace prefix
            if (tag_=='abc'
            and (elt.get('type') in self.locatableTypes)):
                eltAbc = elt # ready to be paired up with a notehead element
            elif tag_=='use':
                attr, val = elt.items()[-1]
                # look for normal note heads and also the special percussion note heads
                if attr.endswith('href'): #  and val.lower() in ('#hd', '#dsh0', '#pshhd', '#pfthd', '#pdshhd', '#pdfthd'):
                    eltHead = elt # ready to be paired up with an 'abc' element
            elif tag_ == 'g':
                tf_ = elt.get('transform')
                if not tf_:
                    continue
                scale_match = re.match('scale\((.*)\)', tf_)
                if scale_match:
                    try:
                        scale_ = float(scale_match.group(1))
                    except ValueError:
                        continue
                    dbg_print("SvgDigest: scale according to g encountered en passant =", scale_)
                continue
            else:
                continue
            if eltAbc is None or eltHead is None:
                continue
# we've 'paired' a note-head and an ABC note description; hurrah!
            sx_ = eltHead.get('x')
            sy_ = eltHead.get('y')
            row_ = int(eltAbc.get('row'))
            col_ = int(eltAbc.get('col'))
            type_ = eltAbc.get('type')
            if not (sx_ and sy_):
                continue
            self.quickDic['x'] = np.append(self.quickDic['x'], scale_ * float(sx_))
            self.quickDic['y'] = np.append(self.quickDic['y'], scale_ * float(sy_))
            self.quickDic['scale'] = np.append(self.quickDic['scale'], scale_)

            self.quickDic['row'] = np.append(self.quickDic['row'], row_)
            self.quickDic['col'] = np.append(self.quickDic['col'], col_)

            self.row_col_dict.setdefault(row_, OrderedDict())[col_] = (eltAbc, eltHead)

            # avoid pairing the same notehead or abc note descripton again!
            eltAbc = eltHead = None
        return

    def insertCursor(self, eltHead, colour='green'):
        self.cursorsDad = eltHead.getparent()
        self.eltCursor = lxml.etree.Element('circle', r='7', stroke=colour,
                          fill="none")
        self.eltCursor.set('stroke-width', '2')
        self.eltCursor.set('cx', eltHead.get('x'))
        self.eltCursor.set('cy', eltHead.get('y'))
        self.cursorsDad.insert(0, self.eltCursor)

        fileName = str(self.svg_file.fileName())
        outFile = open(fileName, 'wb')
        dbg_print('written', fileName)
        self.svg_tree.write(outFile)

    def removeCursor(self):
        if self.eltCursor is not None and self.cursorsDad is not None:
            self.cursorsDad.remove(self.eltCursor)
            self.eltCursor = None

    def rowColAtXY(self, x, y):
        x_dist = x - self.quickDic['x']
        y_dist = y - self.quickDic['y']
        a_dist = x_dist*x_dist + y_dist*y_dist
        am = np.argmin(a_dist)
        row = self.quickDic['row'][am]
        col = self.quickDic['col'][am]
        return row, col
        
class Score(QtGui.QGraphicsView, WithMenu):

    ringColour = 'red'

    menuTag = '&Score'


    def menuItems(self):
        return [
                    ("&Reset Zoom",    'Ctrl+R',      self.resetZoom,),
                    ("&First Page",    'Ctrl+1',      self.showWhichPage,),
                    ("&Next Page",     'Ctrl+PgDown', self.showNextPage,),
                    ("Pre&vious Page", 'Ctrl+PgUp',   self.showPreviousPage,),
                    ('&Print',         'Ctrl+P',      self.printAll,),
                    ('E&xport to PDF', 'Ctrl+Alt+X',  self.printAllToPDF,),
        ]

    def __init__(self):
        dbg_print ("Score.__init__")
        QtGui.QGraphicsView.__init__(self)
        WithMenu.__init__(self)
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
        self.which = 0  # default to show first generated svg until we know better.
        self.fx = self.fy = 0.0
        self.svgDigests = []
        Share.raft.editBook.settledAt.connect(self.showAtRowAndCol)
        Share.abcRaft.midiPlayer.lineAndCol.connect(self.showAtRowAndCol)

        self.svgView = QtWebKit.QGraphicsWebView()
        self.svgView.setFlags(QtGui.QGraphicsItem.ItemClipsToShape)
        self.svgView.setCacheMode(QtGui.QGraphicsItem.NoCache)
        self.svgView.setZValue(0)
        self.prainter = None
        self.svgView.loadFinished.connect(self.svgLoaded)
        self.setScene(MyScene(self))
        self.scene().clear()
        self.scene().addItem(self.svgView)
        self.scene().update()
        dbg_print ("!Score.__init__")

    def svgLoaded(self):
        frame = self.svgView.page().mainFrame()
        fsize = frame.contentsSize()
        self.svgView.resize(QtCore.QSizeF(fsize))
        #print('ensureVisible2 %d %d'  %(self.fx, self.fy))
        #self.ensureVisible(self.fx, self.fy, 1.0, 1.0)
        #self.update()
        if not self.prainter:
            return
        dbg_print ("'prainting' page", self.which)
        if self.which:
            self.printer.newPage()
        else:
            self.prainter.begin(self)
        self.scene().render(self.prainter)
        self.showNextPage()
        if  not self.which:
            self.prainter.end()
            del self.prainter
            self.prainter = None

    def drawBackground42(self, p, rect):
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

    def getEltsOnRow(self, row, which=None):
        if which is True:
            which = self.which
        answer = {}
        for wh, dig in enumerate(self.svgDigests):
            if (which is not None) and (wh!= which):
                continue
            answer.update (self.svgDigests[wh].row_col_dict.setdefault(row, {}))
        return answer

    def showAtRowAndCol(self, row, col):

        Share.eltAbcCursor = None
        dbg_print ('showAtRowAndCol %d %d' %(row, col))
        l = len(self.svgDigests)
        for i in range(l):
            j = (i +self.which) % l
            dictOfRow = self.getEltsOnRow(row, which=j)
            if dictOfRow:
                break
        else:
            dbg_print("can't find page containing svg graphics for row %d"
                      % row)
            return
        self.svgDigests[j].removeCursor()
        for col_ in list(range(col, 0, -1)) + list(range(col, col+5, 1)):
            eltAbc, eltHead = dictOfRow.get(col_, (None, None))
            if isinstance(eltHead, lxml.etree._Element):
                self.fx, self.fy = [float(eltAbc.get(a)) for a in ('x', 'y')]
                self.svgDigests[j].insertCursor(eltHead, colour=self.ringColour)
                break
        else:
            dbg_print("can't find svg graphics correspond to row %d: col %d (page %d)"
                      % (row, col, j))
            self.fx, self.fy = 0.0, 0.0

        # experimental and ugly!
        dbg_print('ensureVisible1 %d %d'  %(self.fx, self.fy))
        self.ensureVisible(self.fx, self.fy, 20.0, 20.0)
        #self.ensureVisible(point.x(), point.y(), 1.0, 1.0)
        self.showWhichPage(j, force=True)
        Share.eltAbcCursor = eltAbc

    def locateXY(self, x, y):
        row, col = self.svgDigests[self.which].rowColAtXY(x, y)
        dbg_print ("locateXY( %d,%d > row,col %d %d" %(x, y, row, col))
        Share.raft.editBook.moveToRowCol(row, col)

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
            raise IOError("'%s' does not exist!" % svg_file.filename())
        self.which = which
        self.svgView.load(QtCore.QUrl(svg_file.fileName()))
        #self.svgDigests[which].AdjustForScene(self.scene())
        self.update()

    def resetZoom(self):
        self.resetTransform()

    def renderAll(self, painter):
        self.prainter = painter
        self.showWhichPage(0, force=True)

    def wheelEvent(self, event):
        dbg_print ("Score.wheelEvent, delta = ", event.delta())
        modifiers = QtGui.QApplication.keyboardModifiers()
        if not (modifiers & QtCore.Qt.ControlModifier):
            # return  self.scrollContentsBy(0, event.delta()*20)
            sbar = self.verticalScrollBar()
            value = sbar.value() - event.delta()
            if event.delta()>0:
                value = max(sbar.minimum(), value)
            else:
                value = min(sbar.maximum(), value)
            sbar.setValue(value)
            dbg_print("%d <= vsbar=%d <= %d" %(sbar.minimum(), value, sbar.maximum()))
            self.update()
            event.accept()
            return
        factor = 1.2**( event.delta() / 120.0)
        self.scale(factor, factor)
        # self.mustApplyTransform = self.transform()
        event.accept()


if __name__ == '__main__':

    class MainWindow(QtGui.QMainWindow):
        """
        warning: not used this '__main__' in months: probably not working!
        """
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
            self.score.useFiles(sys.argv[1:] or
                ['test.svg'])
            self.score.resize(self.score.sizeHint() + QtCore.QSize(
                80, 80 + self.menuBar().height()))


    app = QtGui.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
