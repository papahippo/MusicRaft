#!/usr/bin/python
# -*- encoding: utf8 -*-
"""
Copyright 2015 Hippos Technical Systems BV.

"""
from __future__ import print_function
import os, re,time
from ..share import (Share, dbg_print, QtCore, QtGui, Signal)

X11 = hasattr(QtGui, 'qt_x11_wait_for_window_manager')

class Mark(QtGui.QWidget):

    WIDTH = 12.0
    HEIGHT = 10.0

    def __init__(self, parent=None, ix=0, tag='?', x=0, y=0):
        QtGui.QWidget.__init__(self, parent=parent)
        self.ix = ix
        self.tag = tag
        self.setGeometry(x, y, self.WIDTH, self.HEIGHT)
        self.show()

    def paintEvent(self, event=None):
        painter = QtGui.QPainter(self)
        self.putShape(painter)
        self.putTag(painter)


    def putShape(self, painter):
        triangle = [QtCore.QPointF(0, 0),
                    QtCore.QPointF(self.WIDTH, 0.),
                    QtCore.QPointF(self.WIDTH/2, self.HEIGHT)]
        painter.setPen(QtCore.Qt.blue)
        painter.setBrush(QtCore.Qt.blue)
        painter.drawPolygon(QtGui.QPolygonF(triangle))


    def putTag(self, painter):
        pass  # for now!


    def mousePressEvent(self, event):
        #print('mousePressEvent', self.__class__.__name__, event.x(), self.x())
        self.parent().mousePressEvent(event, child=self)


    def mouseMoveEvent(self, event):
        #print('mouseMoveEvent', self.__class__.__name__, event.x(), self.x())
        self.parent().mouseMoveEvent(event, child=self)

class Bookmark(Mark):
    pass

class TimeMark(Mark):

    WIDTH = 12.0
    HEIGHT = 10.0

    def putShape(self, painter):
        painter.setPen(QtCore.Qt.red)
        painter.setBrush(QtCore.Qt.red)
        painter.drawRect(0., 0., self.WIDTH, self.HEIGHT)


    def putTag(self, painter):
        pass  # for now!

class MarkedSlider(QtGui.QWidget):

    XMARGIN = 12.0
    YMARGIN = 5.0
    WSTRING = "999"
    _value = 0
    _lowest = 0
    _highest = 100
    valueChanged = Signal(int, int)

    def __init__(self, lowest=None, highest=None, value=0, parent=None, client=None):
        QtGui.QWidget.__init__(self, parent=parent)
        self._client = client
        if lowest is not None:
            self._lowest = lowest
        if highest is not None:
            self._highest = highest
        self.setValue(value is not None and value or self._value)
        self.setFocusPolicy(QtCore.Qt.WheelFocus)
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding,
                                       QtGui.QSizePolicy.Fixed))
        self.marks = []
        self.setMarkList([dict(value=self._value, tag='T', Class=TimeMark)])

    def setMarkList(self, markList):
        self.markList = markList
        while self.marks:
            child = self.marks.pop()
            child.hide()
            child.deleteLater()

        for ix, dickie in enumerate(markList):
            Class = dickie.pop('Class', (ix and Bookmark or TimeMark))
            value = dickie.pop('value', 0)
            self.marks.append(Class(parent=self, ix=ix, x= self.xFromValue(value), **dickie))
        self.update()

    def span(self):
        return self.width() - (self.XMARGIN * 2)

    def range(self):
        return (self._highest - self._lowest)

    def xFromValue(self, value):
        return self.XMARGIN + ((value-self._lowest)*self.span()/self.range())

    def valueFromX(self, x):
        return self._lowest + (x-self.XMARGIN)*self.range()/self.span()

    def sizeHint(self):
        return self.minimumSizeHint()

    def minimumSizeHint(self):
        font = QtGui.QFont(self.font())
        font.setPointSize(font.pointSize() - 1)
        fm = QtGui.QFontMetricsF(font)
        return QtCore.QSize(# fm.width(BookmarkedSlider.WSTRING) *
                     # (self.__highest - self.__lowest),
                     480,
                     (fm.height() * 2) + self.YMARGIN)

    def setValue(self, value):
        if self._lowest <= value <= self._highest:
            selfvalue = value
        else:
            raise ValueError("slider value out of range")
        self.update()
        self.updateGeometry()

    def mousePressEvent(self, event, child=None):
        # print ('mousePressEvent', self.__class__.__name__, event.x())
        if event.button() == QtCore.Qt.LeftButton:
            self.mouseMoveEvent(event, child=child)
            event.accept()
        else:
            QtGui.QWidget.mousePressEvent(self, event)

    def mouseMoveEvent(self, event, child=None):
        x = event.x()
        if child is None:
            child = self.marks[0]
        else:
            x += child.x()
        value = self.valueFromX(x)
        # print ('mouseMoveEvent', self.__class__.__name__, x, value)
        child.move(x, child.y())
        self.markList[child.ix]['value'] = value
        # self.valueChanged.emit(child.ix, value)
        self.propagate(value)
        self.update()


    def keyPressEvent(self, event):
        change = 0
        if event.key() == QtCore.Qt.Key_Home:
            change = self.__lowest - self.__value
        elif event.key() in (QtCore.Qt.Key_Up, QtCore.Qt.Key_Right):
            change = 1
        elif event.key() == QtCore.Qt.Key_PageUp:
            change = 10
        elif event.key() in (QtCore.Qt.Key_Down, QtCore.Qt.Key_Left):
            change = -1
        elif event.key() == QtCore.Qt.Key_PageDown:
            change = -10
        elif event.key() == QtCore.Qt.Key_End:
            change = self.__highest - self.__value
        if change:
            value = self.__value
            value += change
            if value != self.__value:
                self.__value = value
               # self.valueChanged.emit(self.__value)
                self.propagate()
                self.update()
            event.accept()
        else:
            QtGui.QWidget.keyPressEvent(self, event)

    def propagate(self, value):
        print ("you should overload this 'propagate' function!")

    def write_to_client(self, s):
        if not self._client:
            return
        self._client.feed_input(s)

    def paintEvent(self, event=None):
        font = QtGui.QFont(self.font())
        font.setPointSize(font.pointSize() - 1)
        fm = QtGui.QFontMetricsF(font)
        fracWidth = fm.width(self.WSTRING)
        indent = fm.boundingRect("9").width() / 2.0
        if not X11:
            fracWidth *= 1.5
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setRenderHint(QtGui.QPainter.TextAntialiasing)
        painter.setPen(self.palette().color(QtGui.QPalette.Mid))
        painter.setBrush(self.palette().brush(
                QtGui.QPalette.AlternateBase))
        painter.drawRect(self.rect())
        segColor = QtGui.QColor(QtCore.Qt.green)  # .dark(120)
        segLineColor = segColor  # .dark()
        painter.setPen(segLineColor)
        painter.setBrush(segColor)
        painter.drawRect(self.XMARGIN,
                         self.YMARGIN, self.span(), fm.height())
        textColor = self.palette().color(QtGui.QPalette.Text)
        segHeight = fm.height() * 2
        nRect = fm.boundingRect(self.WSTRING)
        yOffset = 0 #  segHeight #  + fm.height()
        painter.setPen(QtCore.Qt.yellow)
        painter.setBrush(QtCore.Qt.yellow)
        #value = self.markList[0]['value']
        #x = self.xFromValue(value)
        x = self.marks[0].x()
        painter.drawRect(self.XMARGIN, yOffset, x, fm.height())

class SpeedChanger(MarkedSlider):
    _lowest = 50
    _highest = 200
    _value = 100
    def propagate(self, value):
        print ("setting speed to %u%% of normal value" % value)
        speed =  value / 100.0
        self.write_to_client("speed_set %.2f" % speed)


class PosSeeker(MarkedSlider):
    _lowest = 0
    _highest = 200
    _value = 0
    def propagate(self, value):
        self.write_to_client("seek %u 2" % value)  # absolute position in seconds!



class PlayerControl(QtGui.QWidget):
    headerText = 'player'
    whereDockable = QtCore.Qt.AllDockWidgetAreas
    menu = None

    def __init__(self, parent=None, dock=None, client=None):
        QtGui.QWidget.__init__(self, parent=parent)
        self._client = client
        self.speed_changer = SpeedChanger(client=client)
        # self.pos_seeker = PosSeeker(client=client)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.speed_changer)
        # layout.addWidget(self.pos_seeker)
        self.setLayout(layout)
        # self.setWindowTitle("Sliding")
        # parent.timer.timeout.connect(self.trackPos)

    def trackPos(self):
        percentPos = self._client.percent_pos
        print("trackPos", percentPos)
        # self.pos_seeker.setValue(percentPos)
