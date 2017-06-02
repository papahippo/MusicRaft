#!/usr/bin/python
"""
Copyright 2015 Hippos Technical Systems BV.

@author: larry
"""
from __future__ import print_function
import sys, os, re, subprocess
from ..share import (Share, dbg_print, PlugRaft, QtCore, QtGui, Printer)
from .player_view import PlayerView
from .external import Mplayer, PlayItem
from .control import PlayerControl


class PlayRaft(PlugRaft):

    #myExtensions = ['.mp3', '.mp4', '.wav', '.wma', '.ogg', '.mpg', '.mpeg', '.avi' '.wmv']
    myExtensions = ['.mpl',]

    def __init__(self):
        PlugRaft.__init__(self)
        Share.playRaft = self
        self.playerView = PlayerView()
        self.mplayer = Mplayer()
        self.playerControl = PlayerControl(client=self.mplayer)
        Share.raft.displayBook.addTab(self.playerView, "Player")
        Share.raft.controlBook.widget.addTab(self.playerControl, "Player")

    def checkLoadedFile(self, editor, filename):
        dbg_print('checkLoadedFile', filename)
        if self.isMyType(filename):
            dbg_print(filename + "  ... is a playlist so one of mine!")
