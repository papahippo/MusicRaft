#!/usr/bin/python
"""
Copyright 2015 Hippos Technical Systems BV.
Module 'external' within package 'abcraft' relates to the various
command processors (abc2midi etc.) which are executed by abccraft, and to
their assocated widgets and methods.
"""
from __future__ import print_function
import os, re
from ..share import (Share, dbg_print)
from ..raft.external import External

HTML_PREAMBLE = "Content-type: text/html;charset=UTF-8\n\n"


class Python(External):
    """
class Python -
    """
    fmtNameIn  = '%s.py'
    fmtNameOut = '%s.html'  # ? maybe unused
    exec_dir = '/usr/bin'
    exec_file = 'python3'

    def cmd(self, inF, outF, **kw):
        Share.pyRaft.htmlView.fileName = outF  # quick and dirty fix!
        return External.cmd(self, inF)

    def handle_output(self, output):
        if output.startswith(HTML_PREAMBLE):
            Share.pyRaft.htmlView.showOutput(output[len(HTML_PREAMBLE):])
        else:
            Share.pyRaft.textView.showOutput(output)
        return output
