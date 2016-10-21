#!/usr/bin/python3
"""
Copyright 2015 Hippos Technical Systems BV.

@author: larry
"""
from __future__ import print_function
import sys
import musicraft
print ("imported musicraft package from", musicraft.__file__)
#musicraft.abcraft.external.Abcm2svg.exec_dir = '/usr/local/bin/'
#musicraft.abcraft.external.Abc2midi.exec_dir = '/usr/local/bin/'
musicraft.abcraft.external.Abc2midi.reMsg = r'.*in\s+line-char\s(\d+)\-(\d+).*'
musicraft.raft.main(
    Plugins=(musicraft.abcraft.AbcRaft,
             musicraft.pyraft.PyRaft,
#             musicraft.freqraft.FreqRaft,
             )
)
