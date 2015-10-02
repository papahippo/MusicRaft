#!/usr/bin/python
"""
Copyright 2015 Hippos Technical Systems BV.

@author: larry
"""
from __future__ import print_function
import abcraft
from abcraft.common import (dbg_print, QtCore, QtGui)
dbg_print ("imported abcraft package from", abcraft.__file__)
abcraft.abceditor.AbcEditor.currentLineColor = QtGui.QColor(QtCore.Qt.red).lighter(184)
abcraft.external.Abcm2svg.exe = ('/home/larry/musicprogs/abcm2ps-8.8.4/'
                                'abcm2ps')
abcraft.external.Abcm2svg.reMsg = r'.*:(\d+):(\d+):.*'
abcraft.external.Abc2midi.reMsg = r'.*in\s+line-char\s(\d+)\-(\d+).*'
abcraft.abcraft.main()
