#!/usr/bin/python
"""
Copyright 2015 Hippos Technical Systems BV. This applies only to code written
by the following author...
@author: Larry Myerscough
When a choce has been made between PySide and PyQt4, the above copyright will
be relaxed acordingly.
This python script isintended for use on a 'linux' platform.
It launches the abcraft GUI for ABC(plus) format music notation...
...but it first customizes it to take the all-important abcm2ps
executable and the (also quite important) abc2midi and abc2abc executables from
'local' directories. They will pproably reside here if you have generated them
from source on your own linux system.
"""
from __future__ import print_function
import abcraft
print ("imported abcraft package from", abcraft.__file__)

abcraft.external.Abcm2svg.exe = '/usr/local/bin/abcm2ps'
abcraft.external.Abc2midi.exe = '/usr/local/bin/abc2midi'

# The line below is only necessary if you are using an old version of
# abc2midi which only give line numbers, not line-column pairs in its messages.
#
abcraft.external.Abc2midi.reMsg = r'.*in\s+line\s(\d+)\s\:.*'

print ("running abcraft.main")
abcraft.main()
