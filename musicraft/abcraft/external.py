#!/usr/bin/python
"""
Copyright 2015 Hippos Technical Systems BV.
Module 'external' within package 'abcraft' relates to the various
command processors (abc2midi etc.) which are executed by abccraft, and to
their assocated widgets and methods.
"""
from __future__ import print_function
import re
from ..share import (dbg_print, )
from ..raft.external import External


class Abcm2ps(External):
    """
class Abcm2ps - in our usage - relates only to the use of abcm2ps to produce
postscript (as opposed to svg) output. This is currently unused (see
'Abcm2svg' below.)
    """
    fmtNameIn  = '%s.abc'
    fmtNameOut = '%s.ps'
    exe = 'abcm2ps'
    #exe = '/home/larry/musicprogs/abcm2ps-6.4.1/abcm2ps'

    def cmd(self, inF, outF, **kw):
        return ('%s -O %s %s'
            %(self.exe, outF, inF) )


class Abcm2svg(External):
    
    fmtNameIn  = '%s.abc'
    fmtNameOut = '%s_page_.svg'
    exe = 'abcm2ps'
    reMsg = r'.*in\s+line\s(\d+)\.(\d+).*'
    rowColOrigin = (0, 0)

    def __init__(self):
        External.__init__(self)
        self.outFile_CRE = re.compile("Output written on\s+(\S.*)\s\(.*")

    def cmd(self, inF, outF, **kw):
        return ('%s -v -A -O %s %s'
            %(self.exe, outF, inF) )

    def postProcess(self, error):
        External.postProcess(self, error)
        svgList = []
        for line in error.split('\n'):
            match = self.outFile_CRE.match(line)
            if match:
                svgList.append(match.group(1))
        dbg_print (svgList)
        if svgList and Common.score:
            Common.score.useFiles(svgList)
            # Common.score.showWhichPage(0)


class Abc2midi(External):

    fmtNameIn  = '%s.abc'
    fmtNameOut = '%s.midi'
    exe = '/usr/local/bin/abc2midi'
    errOnOut = True
    reMsg = r'.*in\s+line-char\s(\d+)\-(\d+).*'
    rowColOrigin = (0, 0)
    
    def cmd(self, inF, outF, **kw):
        return ('%s %s -v -EA -o %s'
            %(self.exe, inF, outF) )


class Abc2abc(External):
    
    fmtNameIn  = '%s.abc'
    fmtNameOut = '%.0stransposed.abc'  # sneakily don't use basename at all!
    exe = '/usr/local/bin/abc2abc'
    errOnOut = True
    reMsg = r'(%Warning|%Error).*'

    def cmd(self, inF, outF, transpose=None, **kw):
        flags = ''
        if transpose is not None:
            flags += '-t %d' % transpose
        return ('%s %s -OCC -r %s'
            %(self.exe, inF, flags) )

    def postProcess(self, output_and_error):
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
        print ('error = \n', error)
        External.postProcess(self, error)
        print ('output = \n', output)
        return output
