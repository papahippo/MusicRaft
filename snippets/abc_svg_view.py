#!/usr/bin/env python

"""PyQt4 port of the painting/svgviewer example from Qt v4.x"""

# This is only needed for Python v2 but is harmless for Python v3.
import sip
sip.setapi('QString', 2)
import sys

from PyQt4 import QtCore, QtGui, QtSvg


class MyScene(QtGui.QGraphicsScene):
    def mousePressEvent(self, event):
        print ("MyScene.mousePressEvent",
               event.pos(), event.scenePos(), event.screenPos()
        )

    def wheelEvent(self, event):
        factor = 1.2 #QtCore.qPow(1.2, event.delta() / 240.0)
        self.scale(factor, factor)
        event.accept()


class SvgDigest:
    def __init__(self, filename):
        self.svg_file = QtCore.QFile(filename)
        
class SvgView(QtGui.QGraphicsView):

    def __init__(self, parent=None):
        super(SvgView, self).__init__(parent)

        self.svgItem = None
        self.backgroundItem = None
        self.outlineItem = None
        self.image = QtGui.QImage()

        self.setScene(MyScene(self))
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)


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


            self.showWhichFile(0)

    def showWhichFile(self, which):
        svg_file = self.svgDigests[which].svg_file
        if not svg_file.exists():
            raise IOError, ("'%s' does not exist!" % svg_file.filename())

        s = self.scene()

        s.clear()
        self.resetTransform()

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

        s.setSceneRect(self.outlineItem.boundingRect()) 
        # .adjusted(-10, -10, 10, 10))

        self.setViewport(QtGui.QWidget())

        self.backgroundItem.setVisible(True)
        self.outlineItem.setVisible(False)


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.currentPath = ''

        self.view = SvgView()

        fileMenu = QtGui.QMenu("&File", self)
        quitAction = fileMenu.addAction("E&xit")
        quitAction.setShortcut("Ctrl+Q")

        self.menuBar().addMenu(fileMenu)


        quitAction.triggered.connect(QtGui.qApp.quit)

        self.setCentralWidget(self.view)
        self.setWindowTitle("SVG Viewer")
        self.view.useFiles(sys.argv[1:] or ['./dp_page_001.svg', ])
        self.resize(self.view.sizeHint() + QtCore.QSize(80, 80 + self.menuBar().height()))


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
