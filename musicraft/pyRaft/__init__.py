#!/usr/bin/python
"""
Copyright 2015 Hippos Technical Systems BV.

@author: larry
"""
from __future__ import print_function
import sys, os, re, subprocess
from ..share import (Share, QtCore, QtGui, Printer)
from .html_view import HtmlView
from .external import (Python)

class PyRaft(QtGui.QMainWindow):

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Share.abcRaft = self
        self.htmlView = HtmlView()
        self.python = Python()
        Share.raft.displayBook.addTab(self.htmlView, "HTML")


    def start_midi(self):
        if not (self.abc2midi and self.abc2midi.outFileName):
            return
        if self.midiPlayer:
           self.midiPlayer.play(self.abc2midi.outFileName)

    def pause_midi(self):
        if self.midiPlayer:
           self.midiPlayer.pause()

    def create_actions(self):
        self.start_midi_action = Share.raft.myQAction("Start &Midi",shortcut="Ctrl+M",
                triggered=self.start_midi)

        self.pause_midi_action = myQAction("Pause M&idi",shortcut="Ctrl+,",
                triggered=self.pause_midi)

    def create_menus(self):

        self.midi_menu = QtGui.QMenu("&Midi", self)
        self.midi_menu.addAction(self.start_midi_action)
        self.midi_menuMenu.addAction(self.pause_midi_action)

        Share.raft.menuBar().addMenu(self.midi_menu)
        Share.raft.menuBar().show()
