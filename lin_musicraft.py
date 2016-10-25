#!/away/larry/python/fromGit/abcraft/venv.python3.4/bin/python3
#!/usr/bin/env python3
"""
Copyright 2015 Hippos Technical Systems BV.

@author: larry
"""
from __future__ import print_function
import sys
import musicraft
print ("imported musicraft package from", musicraft.__file__)
musicraft.abcraft.external.Abcm2svg.exec_dir = '/away/larry/musicprogs/abcm2ps-8.8.5/'
musicraft.abcraft.external.Abc2midi.exec_dir = '/usr/local/bin/'
musicraft.abcraft.external.Abc2midi.reMsg = r'.*in\s+line-char\s(\d+)\-(\d+).*'
musicraft.raft.main(
    Plugins=(musicraft.abcraft.AbcRaft,
             musicraft.pyraft.PyRaft,
             # musicraft.freqraft.FreqRaft,
             )
)
