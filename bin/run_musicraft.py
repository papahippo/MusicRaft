#!/usr/bin/env python3
###!/home/gill/python/fromGit/abcraft/venv.python3.4/bin/python
"""
Copyright 2015 Hippos Technical Systems BV.

@author: larry
"""
from __future__ import print_function
import sys
import musicraft
print ("imported musicraft package from", musicraft.__file__)

# Below are examples of how to 'doctor' the behaviour of musicraft.
# This can be handy if e.g. you've installed a newer version of abcm2ps than that on the standard path.
#
#musicraft.abcraft.external.Abcm2svg.exec_dir = '/usr/local/bin/'
#musicraft.abcraft.external.Abc2midi.exec_dir = '/usr/local/bin/'
#musicraft.abcraft.external.Abc2midi.reMsg = r'.*in\s+line-char\s(\d+)\-(\d+).*'
#
# uncomment (and maybve adjust) the above lines only if you need to 'doctor' the behaviour of musicraft.

# call the 'raft' with just the 'musicraft' plugin; other optional experimental plugins are currently disabled.
#
musicraft.raft.main(
    Plugins=(musicraft.abcraft.AbcRaft,
             musicraft.pyraft.PyRaft,
           #  musicraft.freqraft.FreqRaft,
             )
)
