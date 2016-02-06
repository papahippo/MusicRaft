#!/usr/bin/python3
"""
Copyright 2015 Hippos Technical Systems BV.

@author: larry
"""
from __future__ import print_function
import sys
print (sys.path)

import musicraft
print (dir(musicraft))
print ("imported musicraft package from", musicraft.__path__)
print ("running raft.main")
musicraft.raft.main()
