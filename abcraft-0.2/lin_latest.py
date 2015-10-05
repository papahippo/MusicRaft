#!/usr/bin/python
"""
Copyright 2015 Hippos Technical Systems BV.

@author: larry
"""
from __future__ import print_function
import abcraft
print ("imported abcraft package from", abcraft.__file__)

# The ugly use of a 'fudge factor' makes the "click-on-note to show ABC source
# cursor" work. I'm still looking for a sounder algorithm for this!
#
abcraft.score.SvgDigest.gScaleMultiplier = 1.25

abcraft.external.Abcm2svg.exe = ('/home/larry/musicprogs/abcm2ps-8.8.5/'
                                 'abcm2ps')
abcraft.abcraft.main()
