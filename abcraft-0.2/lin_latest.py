#!/usr/bin/python
"""
Copyright 2015 Hippos Technical Systems BV.

@author: larry
"""
from __future__ import print_function
import abcraft
print ("imported abcraft package from", abcraft.__file__)

abcraft.external.Abcm2svg.exe = ('/home/larry/musicprogs/abcm2ps-8.9.0/'
                                 'abcm2ps')
abcraft.external.Abcm2svg.reMsg = r'.*\:(\d+)\:(\d+)\:.*'
abcraft.abcraft.main()
