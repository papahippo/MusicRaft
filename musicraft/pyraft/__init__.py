#!/usr/bin/python
"""
Copyright 2015 Hippos Technical Systems BV.

@author: larry
"""
from __future__ import print_function
import sys, os, re, subprocess
from ..share import (Share, dbg_print, QtCore, QtGui, Printer)
from .html_view import HtmlView
from .text_view import TextView
from .external import Python
from .syntax import PythonHighlighter


class PyRaft(object):

    def __init__(self):
        Share.pyRaft = self
        self.htmlView = HtmlView()
        self.textView = TextView()
        self.python = Python()
        Share.raft.displayBook.addTab(self.htmlView, "Html")
        Share.raft.displayBook.addTab(self.textView, "Text")
        Share.raft.editor.fileLoaded.connect(self.checkLoadedFile)

    def checkLoadedFile(self, filename):
        dbg_print('checkLoadedFile', filename)
        if os.path.splitext(filename)[1] in ('.py', '.pyw'):
            dbg_print(filename + "  ... is one of mine!")
            highlight = syntax.PythonHighlighter(Share.raft.editor.activeEdit.document())
