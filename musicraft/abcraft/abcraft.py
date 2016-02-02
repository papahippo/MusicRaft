#!/usr/bin/python
"""
Copyright 2015 Hippos Technical Systems BV.

@author: larry
"""
from __future__ import print_function
import sys, os, re, subprocess
from .abceditor import AbcEditor
from .score import Score
from .common import (QtCore, QtGui, Common,
                    Printer, myQAction, widgetWithMenu, dbg_print)
                    
from .external import (Abc2midi, Abcm2svg, Abc2abc) 
from .midiplayer import MidiPlayer


class AbcRaft(QtGui.QMainWindow):

    midiPlayerExe = 'timidity'

    def __init__(self, raft):
        self.raft = raft
        self.abc2abc = Abc2abc(raft)
        self.abc2midi = Abc2midi(raft)
        self.abcm2svg = Abcm2svg(raft)
       
        self.midiPlayer = MidiPlayer(raft)
        self.printer = Printer(raft)

        self.score = Score(raft)
        raft.setCentralWidget(self.score)
        raft.setWindowTitle("ABCraft")
        self.resize(1280, 1024)
        self.create_actions()
        self.create_menus()

    def start_midi(self):
        if not (self.abc2midi and self.abc2midi.outFileName):
            return
        if self.midiPlayer:
           self.midiPlayer.play(self.abc2midi.outFileName)

    def pause_midi(self):
        if self.midiPlayer:
           self.midiPlayer.pause()

    def create_actions(self):
        self.start_midi_action = self.raft.myQAction("Start &Midi",shortcut="Ctrl+M",
                triggered=self.start_midi)

        self.pause_midi_action = myQAction("Pause M&idi",shortcut="Ctrl+,",
                triggered=self.pause_midi)

    def create_menus(self):

        self.midi_menu = QtGui.QMenu("&Midi", self)
        self.midi_menu.addAction(self.start_midi_action)
        self.midi_menuMenu.addAction(self.pause_midi_action)

        self.raft.menuBar().addMenu(self.midi_menu)
        self.raft.menuBar().show()

def main():
    app = QtGui.QApplication(sys.argv)
    abcCraft = AbcRaft()
    abcCraft.show()
    try:
        sys.exit(app.exec_())
    except:
        pass

if __name__ == '__main__':
    main()
