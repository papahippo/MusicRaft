#!/usr/bin/python
"""
Copyright 2015 Hippos Technical Systems BV.

@author: larry
"""
from __future__ import print_function
import sys, os, re, subprocess
from ..share import (Share, dbg_print, QtCore, QtGui, Printer)
from .freq_view import FreqView


class FreqRaft(object):

    def __init__(self):
        Share.pyRaft = self
        self.freqView = FreqView()
        Share.raft.displayBook.addTab(self.freqViewView, "Tuning")

