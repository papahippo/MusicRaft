#!/usr/bin/python
"""
Copyright 2015 Hippos Technical Systems BV.

@author: larry
"""
from __future__ import print_function
import sys, os, re, subprocess
from ..share import (Share, dbg_print, PlugRaft, QtCore, QtGui, Printer)
from .player_view import PlayerView
from .external import Mplayer


class PlayRaft(PlugRaft):

    myExtensions = ['.mp3', '.mp4', '.wav', '.wma', '.ogg', '.mpg', '.mpeg', '.avi' '.wmv']

    def __init__(self):
        PlugRaft.__init__(self)
        Share.playyRaft = self
        self.htmlView = HtmlView()
        self.textView = TextView()
        self.python = Python()
        Share.raft.displayBook.addTab(self.htmlView, "Html")
        Share.raft.displayBook.addTab(self.textView, "Text")
        Share.raft.editBook.fileLoaded.connect(self.checkLoadedFile)

    def checkLoadedFile(self, editor, filename):
        dbg_print('checkLoadedFile', filename)
        if self.isMyType(filename):
            dbg_print(filename + "  ... is one of mine!")
            editor.highlighter = syntax.PythonHighlighter(editor.document())
