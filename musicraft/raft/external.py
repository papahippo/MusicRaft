#!/usr/bin/python
"""
Copyright 2015 Hippos Technical Systems BV.
Module 'external' within package 'abcraft' relates to the various
command processors (abc2midi etc.) which are executed by abccraft, and to
their assocated widgets and methods.
"""
from __future__ import print_function
import logging
logger = logging.getLogger()
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
    fmtNameIn  = '%s.in'
    fmtNameOut = '%s.out'
    exec_dir = os.path.normpath(os.path.split(__file__)[0] + '/../share/' + os.sys.platform + '/bin').replace(
        'linux2', 'linux')
    #exec_dir = os.path.normpath(os.path.split(__file__)[0] + '/../share/' + os.sys.platform + '/bin')
    exec_file = "base_class_stub_of_exec_file"
    outFileName = None
    errOnOut = False
    reMsg = r'$^'  # default = don't match any lines.
    rowColOrigin = (0, -1)
    stdFont = 'Courier New', 10, False


    def __init__(self):
        self.creMsg = re.compile(self.reMsg)
        self.stdTab = StdTab(self)
        Share.raft.stdBook.widget.addTab(self.stdTab,
                                     self.__class__.__name__)
        Share.raft.stdBook.widget.setCurrentWidget(self.stdTab)
        Share.raft.editor.fileSaved.connect(self.process)

    def cmd(self, *pp):
        answer = ' '.join((os.path.sep.join((self.exec_dir, self.exec_file)),) + pp)
        dbg_print ("External.cmd answer = ", answer)
        return answer

    def process_output(self, output):
        return output

    def process(self, inFileName, **kw):
        baseName = os.path.splitext(inFileName)[0]
        if inFileName != (self.fmtNameIn % baseName):
            logger.warning("ignoring file {0} (doesn't conform to '{1}'".format(
                                        inFileName,             self.fmtNameIn))
            return
        self.outFileName = self.fmtNameOut % baseName
        if self.cmd is None:
            return

        cmd1 = self.cmd(inFileName, self.outFileName, **kw)
        dbg_print (cmd1)
        process = subprocess.Popen(cmd1, stdout=subprocess.PIPE, shell=True,
            stderr= subprocess.STDOUT if self.errOnOut else subprocess.PIPE)
        output_bytes, error_bytes = process.communicate()
        output = output_bytes and output_bytes.decode()
        error = error_bytes and error_bytes.decode()
        _retcode = process.poll()
        if _retcode:
            pass
        #    raise subprocess.CalledProcessError(retcode,
        #                                        cmd1, output=output)
        if self.errOnOut:
            dbg_print ('output = \n', output)
            return self.process_error(output)
        else:
            self.process_error(error)
            return self.process_ouput(output)

    def process_error(self, error):
        if self.stdTab is None:
            dbg_print ("self.stdTab is None!")
        else:
            self.stdTab.setPlainText(error)
