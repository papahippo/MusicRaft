#!/usr/bin/python
"""
Copyright 2015 Hippos Technical Systems BV.

@author: larry
"""
from __future__ import print_function
import sys, os, re, subprocess
from ..share import (Share, QtCore, QtGui, Printer, dbg_print)
from .score import Score
from .syntax import AbcHighlighter

from .external import (Abc2midi, Abcm2svg, Abc2abc)

from .midiplayer import MidiPlayer


class AbcRaft(object):

    midiPlayerExe = 'timidity'

    def __init__(self):
        Share.abcRaft = self
        self.midiPlayer = MidiPlayer()
        self.score = Score()
        self.abc2abc = Abc2abc()
        self.abc2midi = Abc2midi()
        self.abcm2svg = Abcm2svg()

        self.printer = Printer()

        Share.raft.setWindowTitle("Musicraft")
        Share.raft.displayBook.addTab(self.score, "Score")
        Share.raft.editBook.fileLoaded.connect(self.checkLoadedFile)

        self.create_actions()
        self.create_menus()

    def checkLoadedFile(self, editor, filename):
        dbg_print('checkLoadedFile', filename)
        if os.path.splitext(filename)[1] in ('.abc', '.ABC'):
            dbg_print("we expect ABC syntax in " + filename)
            editor.highlighter = syntax.AbcHighlighter(editor.document(), editor)

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

        self.pause_midi_action = Share.raft.myQAction("Pause M&idi",shortcut="Ctrl+,",
                triggered=self.pause_midi)

    def create_menus(self):

        self.midi_menu = QtGui.QMenu("&Midi")
        self.midi_menu.addAction(self.start_midi_action)
        self.midi_menu.addAction(self.pause_midi_action)

        Share.raft.menuBar().addMenu(self.midi_menu)
        Share.raft.menuBar().show()
