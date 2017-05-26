#!/usr/bin/python
# -*- encoding: utf8 -*-
"""
Copyright 2015 Hippos Technical Systems BV.
Module 'external' within package 'abcraft' relates to the various
command processors (abc2midi etc.) which are executed by abccraft, and to
their assocated widgets and methods.
"""
from __future__ import print_function
import os, re,time
from ..share import (Share, dbg_print, QtCore, QtGui)
from ..raft.external import External

HTML_PREAMBLE = "Content-type: text/html"

#FUDGED_FILENAME = '/away/larry/Music/01.ShiftinBobbins_8x32R.mp3'
FUDGED_FILENAME = '/home/gill/test.mp4'

class NonblockingReader():
  def __init__(self, pipe):
    self.fd = pipe.fileno()
    self.buffer = b''

  def readlines(self):
      self.buffer += os.read(self.fd, 2048)
      lines = self.buffer.split(bytes(os.linesep, 'utf8'))
      self.buffer = lines[-1]
      return lines[:-1]

class Mplayer(External):
    """
class Python -
    """
    fmtNameIn  = '%s.mpl'
    #fmtNameOut = '%s.html'  # ? maybe unused
    exec_dir = '/usr/bin/'
    exec_file = 'mplayer'
    errOnOut = True
    msPoll   = 20

    def cmd(self, inF, outF, **kw):
        self._inF = inF
        return External.cmd(self, '-slave', '-idle', # '-really-quiet', '-msglevel', 'global=4',
                  '-input', 'nodefault-bindings', '-noconfig', 'all',)
                  #'-msglevel', 'global=6', '-fixed-vo', '-fs',)
                  #'-wid', str(Share.playRaft.playerView.winId()))

    def manage(self):
        self.non_blocking_pipe = NonblockingReader(self._process.stdout)
        self.feed_input("loadfile %s" % FUDGED_FILENAME)
        self.poll_output()

    def poll_output(self):
        if self._process.poll() is not None:
            print (self._process.poll())
            return External.manage(self)
        for line in self.non_blocking_pipe.readlines():
            self.stdTab.appendPlainText(line.decode())
        QtCore.QTimer.singleShot(self.msPoll, self.poll_output)

    def feed_input(self, s):
        self._process.stdin.write(bytes(s +"\n", 'utf8'))
        self._process.stdin.flush()

    def handle_output(self, output):
        return output  # to be completed!
