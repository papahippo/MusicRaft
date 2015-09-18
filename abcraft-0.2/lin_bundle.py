#!/usr/bin/python
"""
Copyright 2015 Hippos Technical Systems BV.

@author: larry
"""
from __future__ import print_function
import os
import abcraft
print ("imported abcraft package from", abcraft.__file__)

# This script assumes you wish to use the versions of the executables
# for abcm2ps etc. which reside in the .../share/bin subdirectory of
# the package tree.
shareBinDir = os.path.normpath(
    os.path.split(abcraft.__file__)[0] + '../../share/linux/bin'
)
# Usually the stable version of abcm2ps (etc.) will be accessible as simply
# 'abcn2ps', so (e..g.) 'abcraft.external.Abcm2svg.exe' wil not need to be
# customized. Otherwise, uncomment (remove the '#') line below and edit
# teh pat as appropriate.
#
abcraft.external.Abcm2ps.exe = shareBinDir + '/abcm2ps'
# note that our notional 'Abcm2svg' actually runs abcm2ps!
abcraft.external.Abcm2svg.exe = shareBinDir + '/abcm2ps'
abcraft.external.Abc2midi.exe = shareBinDir + '/abc2midi'
abcraft.external.Abc2abc.exe = shareBinDir + '/abc2midi'

abcraft.abcraft.main()
