#!/usr/bin/python
# -*- encoding: utf8 -*-
"""
Copyright 2015 Hippos Technical Systems BV.

"""
from __future__ import print_function
import os, re,time
from ..share import (Share, dbg_print, QtCore, QtGui)


class SliderPlus(QtGui.QGroupBox):
    _minimum = 25
    _maximum = 400
    _value = 100
    single_step = 1
    tick_interval = 10
    tick_position = QtGui.QSlider.TicksBothSides
    _orientation = QtCore.Qt.Vertical
    focus_policy = QtCore.Qt.StrongFocus

    def __init__(self, orientation, title, parent=None, client=None):
        QtGui.QGroupBox.__init__(self, title, parent)
        self._client = client
        self.slider = QtGui.QSlider(orientation)
        self.slider.setFocusPolicy(self.focus_policy)
        self.slider.setTickPosition(self.tick_position)
        self.slider.setTickInterval(self.tick_interval)
        self.slider.setSingleStep(self.single_step)
        self.slider.setMinimum(self._minimum)
        self.slider.setMaximum(self._maximum)
        self.slider.setValue(100)
        self.slider.valueChanged.connect(self.reactToSlide)

        if orientation == QtCore.Qt.Horizontal:
            direction = QtGui.QBoxLayout.TopToBottom
        else:
            direction = QtGui.QBoxLayout.LeftToRight

        slidersLayout = QtGui.QBoxLayout(direction)
        slidersLayout.addWidget(self.slider)
        self.setLayout(slidersLayout)

    def write_to_client(self, s):
        if not self._client:
            return
        self._client.feed_input(s)

    def reactToSlide(self, value):
        print('slid to', value)
        self.adjust(value)

    def adjust(self, value):
        print("don't call me directly")

    def setValue(self, value):
        if not self.slider.isSliderDown():
            self.slider.setSliderPosition(value)


class SpeedChanger(SliderPlus):
    def adjust(self, value):
        #if self._client:
        #    # self._client.speed = value / 100.0
        speed =  value / 100.0
        self.write_to_client("speed_set %.2f" % speed)

class PosSeeker(SliderPlus):
    _minimum = 0
    _maximum = 100
    _value = 100
    tick_interval = 10

    def adjust(self, value):
        if self._client:
            self._client.percent_pos = value


class PlayerControl(QtGui.QWidget):
    headerText = 'player'
    whereDockable = QtCore.Qt.AllDockWidgetAreas
    menu = None

    def __init__(self, parent=None, dock=None, client=None):
        QtGui.QWidget.__init__(self, parent=parent)
        self._client = client
        self.speed_changer = SpeedChanger(QtCore.Qt.Horizontal, "Speed", client=client)
        self.pos_seeker = PosSeeker(QtCore.Qt.Horizontal, "Position", client=client)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.speed_changer)
        layout.addWidget(self.pos_seeker)
        self.setLayout(layout)
        # self.setWindowTitle("Sliding")
        # parent.timer.timeout.connect(self.trackPos)

    def trackPos(self):
        percentPos = self._client.percent_pos
        print("trackPos", percentPos)
        # self.pos_seeker.setValue(percentPos)
