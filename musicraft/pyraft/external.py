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


class Python(External):
    """
class Python -
    """
    fmtNameIn  = '%s.py'
    fmtNameOut = '%s.html'  # ? maybe unused
    exec_dir = '/usr/bin'
    exec_file = 'python'

    def cmd(self, inF, outF, **kw):
        return External.cmd(self, inF)

    def handle_output(self, output):
        Share.pyRaft.htmlView.showOutput(output)
        return output
