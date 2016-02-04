#!/usr/bin/python
"""
Copyright 2015 Hippos Technical Systems BV.
Module 'external' within package 'abcraft' relates to the various
command processors (abc2midi etc.) which are executed by abccraft, and to
their assocated widgets and methods.
"""
from __future__ import print_function
import os, re, subprocess
from ..share import (Share, dbg_print, QtGui)


class StdTab(QtGui.QPlainTextEdit):
    """
This now very bare looking class will be embellished with facilities for
error location helpers etc. in due course. It is the class behind the several
tabs (Abcm2svg etc.) within the subprocess output notebook.
    """
    def __init__(self, commander):
        QtGui.QPlainTextEdit.__init__(self)
        font = QtGui.QFont(*commander.stdFont)
        self.setFont(font)
        dbg_print (self.__class__.__name__+':__init__... commander.reMsg =',
               commander.reMsg)
        self.creMsg = commander.creMsg
        self.rowColOrigin = commander.rowColOrigin
        self.quiet = False
        self.cursorPositionChanged.connect(self.handleCursorMove)

    def handleCursorMove(self):
        dbg_print (self.__class__.__name__+':handleCursorMove... self.quiet =',
               self.quiet)
        if self.quiet:
            return
        match = self.creMsg.match(self.textCursor().block().text())
        dbg_print (self.__class__.__name__+':handleCursorMove... match =', match)
        if match is None:
            return
        location = [o1+o2 for (o1, o2) in zip(
                        map(lambda s: int(s), match.groups()),
                       self.rowColOrigin)]

        print ("Autolocating error in ABC", location )
        
        Share.raft.editor.moveToRowCol(*location)

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
    stdFont = 'Courier New', 10, False


    def __init__(self):
        dbg_print ("External __init__", self.__class__.__name__,
                   self.fmtNameIn, self.fmtNameOut)
        self.creMsg = re.compile(self.reMsg)
        self.stdTab = StdTab(self)
        Share.raft.stdBook.widget.addTab(self.stdTab,
                                     self.__class__.__name__)
        Share.raft.stdBook.widget.setCurrentWidget(self.stdTab)
        Share.raft.editor.fileSaved.connect(self.process)

    def process(self, inFileName, **kw):
        print ("External", self.cmd, kw, "run on", inFileName,
               self.fmtNameIn)
        baseName = os.path.splitext(inFileName)[0]
        if inFileName != (self.fmtNameIn % baseName):
            raise TypeError ("%s cannot handle this filetype: %s" %
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
                dbg_print ('output = \n', output)
                return self.postProcess(output)
            else:
                self.postProcess(error)
                return output

    def postProcess(self, error):
        if self.stdTab is None:
            dbg_print ("self.stdTab is None!")
        else:
            self.stdTab.setPlainText(error)
