#!/usr/bin/python
"""
Copyright 2015 Hippos Technical Systems BV.

@author: larry
"""
from bundle import Bundle

class AbcraftBundle(Bundle):
    target_package = 'abcraft'
    needs = (
        ('PySide', None),
        ('lxml', None),
        ('numpy', "http://sourceforge.net"
                  "/projects/numpy/files/NumPy/1.7.0/"
                  "numpy-1.7.0-win32-superpack-python2.7.exe"),
    )
    runners = {
        'win32': 'win_abcraft.py',
        'linux2': 'lin_abcraft.py',
    }

if __name__ == '__main__':  # in practivce, always the case?
    AbcraftBundle().install()
