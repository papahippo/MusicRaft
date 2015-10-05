#!/usr/bin/python
"""
Copyright 2015 Hippos Technical Systems BV.
Module 'external' within package 'abcraft' relates to the various
command processors (abc2midi etc.) which are executed by abccraft, and to
their assocated widgets and methods.
"""
from __future__ import print_function
import os, re, subprocess
from common import (Common, dbg_print,
                    QtGui)


class StdTab(QtGui.QPlainTextEdit):
    """
This now very bare looking class will be embellished with facilities for
error location helpers etc. in due course. It is the class behind the several
tabs (Abcm2svg etc.) within the subprocess output notebook.
    """
    def __init__(self, commander=None):
        QtGui.QPlainTextEdit.__init__(self)
        dbg_print (self.__class__.__name__+':__init__... commander.reMsg =',
               commander.reMsg)
        self.creMsg = re.compile(commander.reMsg)
        self.rowColOrigin = commander.rowColOrigin
        self.quiet = False
        self.cursorPositionChanged.connect(self.handleCursorMove)

    def handleCursorMove(self):
        dbg_print (self.__class__.__name__+':handleCursorMove... self.quiet =',
               self.quiet)
        if (Common.abcEditor is None) or self.quiet:
            return
        match = self.creMsg.match(self.textCursor().block().text())
        dbg_print (self.__class__.__name__+':handleCursorMove... match =', match)
        if match is None:
            return
        location = [o1+o2 for (o1, o2) in zip(
                        map(lambda s: int(s), match.groups()),
                       self.rowColOrigin)]

        print ("Autolocating error in ABC", location )
        
        Common.abcEditor.widget.moveToRowCol(*location)

    def setPlainText(self, text):
        self.quiet = True
        QtGui.QPlainTextEdit.setPlainText(self, text)
        self.quiet = False
    
class External(object):
    """
'External' is the generic class representing command processors invoked from
within abcraft.
    """
    cmd = 'echo'  # just a stub which might be useful
    fmtNameIn  = '%s.in'
    fmtNameOut = '%s.out'
    exe = None
    outFileName = None
    errOnOut = False
    reMsg = r'$^'  # default = don't match any lines.
    rowColOrigin = (0, -1)

    def __init__(self):
        dbg_print ("External __init__", self.fmtNameIn, self.fmtNameOut)
        if Common.stdBook is None:
            dbg_print ("what? no Common.stdBook")
            self.stdTab = None
        else:
            self.stdTab = StdTab(self)
            Common.stdBook.widget.addTab(self.stdTab,
                                         self.__class__.__name__)

    def process(self, inFileName, **kw):
        dbg_print ("External", self.cmd, kw, "run on", inFileName,
               self.fmtNameIn)
        baseName = os.path.splitext(inFileName)[0]
        if inFileName != (self.fmtNameIn % baseName):
            raise TypeError, ("%s cannot handle this filetype: %s" %
                             (self.fmtNameIn,  baseName, self.__class__.__name__,     inFileName))
        self.outFileName = self.fmtNameOut % baseName
        if self.cmd is not None:
            cmd1 = self.cmd(inFileName, self.outFileName, **kw)
            dbg_print (cmd1)
            if self.errOnOut:
                stderr = subprocess.STDOUT
            else:
                stderr = subprocess.PIPE
            process = subprocess.Popen(cmd1, stdout=subprocess.PIPE,
                                             stderr=stderr,
                                             shell=True)
            output, error = process.communicate()
            _retcode = process.poll()
            if _retcode:
                pass
            #    raise subprocess.CalledProcessError(retcode,
            #                                        cmd1, output=output)
            
            if self.errOnOut:
                self.postProcess(output)
                return None
            else:
                self.postProcess(error)
                return output

    def postProcess(self, error):
        if self.stdTab is None:
            dbg_print ("self.stdTab is None!")
        else:
            self.stdTab.setPlainText(error)
                
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

    def cmd(self, inF, outF, transpose=None, **kw):
        flags = ''
        if transpose is not None:
            flags += '-t %d' % transpose
        return ('%s %s -OCC -r %s'
            %(self.exe, inF, flags) )

