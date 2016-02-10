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


class Abcm2ps(External):
    """
class Abcm2ps - in our usage - relates only to the use of abcm2ps to produce
postscript (as opposed to svg) output. This is currently unused (see
'Abcm2svg' below.)
    """
    fmtNameIn  = '%s.abc'
    fmtNameOut = '%s.ps'
    exec_file = 'abcm2ps'

    def cmd(self, inF, outF, **kw):
        return External.cmd(self, '-A', '-O', outF, inF)


class Abcm2svg(External):
    
    fmtNameIn  = '%s.abc'
    fmtNameOut = '%s_page_.svg'
    exec_file = 'abcm2ps'
    reMsg = r'.*in\s+line\s(\d+)\.(\d+).*'
    rowColOrigin = (0, 0)

    def __init__(self):
        External.__init__(self)
        self.outFile_CRE = re.compile("Output written on\s+(\S.*)\s\(.*")

    def cmd(self, inF, outF, **kw):
        return External.cmd(self, '-v -A -O', outF, inF)

    def handle_output(self, output):
        return output

    def process_error(self, error):
        External.process_error(self, error)
        svgList = []
        for line in error.split('\n'):
            match = self.outFile_CRE.match(line)
            if match:
                svgList.append(match.group(1))
        dbg_print (svgList)
        if svgList:
            Share.abcRaft.score.useFiles(svgList)
            # Share.abcRaft.score.showWhichPage(0)


class Abc2midi(External):

    fmtNameIn  = '%s.abc'
    fmtNameOut = '%s.midi'
    exec_file = 'abc2midi'
    errOnOut = True
    reMsg = r'.*in\s+line-char\s(\d+)\-(\d+).*'
    rowColOrigin = (0, 0)
    
    def cmd(self, inF, outF, **kw):
        return External.cmd(self, inF, '-v', '-EA', '-o', outF)


class Abc2abc(External):
    
    fmtNameIn  = '%s.abc'
    fmtNameOut = '%.0stransposed.abc'  # sneakily don't use basename at all!
    exec_file = 'abc2abc'
    errOnOut = True
    reMsg = r'(%Warning|%Error).*'

    def cmd(self, inF, outF, transpose=None, **kw):
        pp = [inF, '-OCC', '-r']
        if transpose is not None:
            pp += ['-t', str(transpose)]
        return External.cmd(self, *pp)

    def process_error(self, output_and_error):
        error = ''
        output = ''
        for line in output_and_error.split('\n'):
            if self.creMsg.match(line):
                output = output[:-1]
                output_and_error = output_and_error[1:]
                error += ('line %d: ' % output.count('\n') + line + '\n')
                
            else:
                output += (line + '\n')
        self.stdTab.creMsg = re.compile(r'.*line\s+(\d+)\:.*')
        # print ('error = \n', error)
        External.process_error(self, error)
        # print ('output = \n', output)
        return output
