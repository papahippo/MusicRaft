#!/usr/bin/python
"""
Copyright 2015 Hippos Technical Systems BV.

@author: larry
"""
from __future__ import print_function
import sys
import numpy
import pyaudio
from ..share import (Share, dbg_print, QtCore, QtGui, Printer)
from ..raft.external import StdTab
from .terpsichore import default_voice
from .pitch_view import PitchView


class FreqRaft(object):
    inputDeviceIndex = 0
    creMsg = reMsg = None  # to be reviewed - nec. for StdTab
    stdFont = 'Courier New', 10, False  # likewise!
    rowColOrigin = (0, -1)  # also likewise!

    def __init__(self):
        Share.freqRaft = self
# following code cribbed from source code of myPlot1.py:
        self.pitch_view = PitchView()
        Share.raft.displayBook.addTab(self.pitch_view, "Tuning")
        self.stdTab = StdTab(self)
        Share.raft.stdBook.widget.addTab(self.stdTab,
                                     'frequency')

    def write(self, text):
        self.stdTab.appendPlainText(str(text))
        #print(text)

