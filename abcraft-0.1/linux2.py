#!/usr/bin/python
"""
Copyright 2015 Hippos Technical Systems BV.

@author: larry
"""
from __future__ import print_function
import abcraft
print ("imported abcraft package from", abcraft.__file__)
abcraft.external.Abcm2svg.exe = '/usr/local/bin/abcm2ps'
abcraft.external.Abc2midi.exe = '/usr/local/bin/abc2midi'
abcraft.external.Abc2midi.reMsg = r'.*in\s+line-char\s(\d+)\-(\d+).*'

abcraft.main()
