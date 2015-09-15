#!/usr/bin/python
"""
Copyright 2015 Hippos Technical Systems BV.

@author: larry
"""
from __future__ import print_function
import abcraft
print ("imported abcraft package from", abcraft.__file__)
abcraft.external.Abcm2svg.exe = '/home/larry/musicprogs/abcm2ps-7.8.14/abcm2ps'
abcraft.abcraft.main()
