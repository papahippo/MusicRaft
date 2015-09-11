#!/usr/bin/python
import sys, os
import abcraft
print ("imported abcraft package from", abcraft.__file__)

# using correct (backward) slashes for Windows platforms is not really
# necesary in python but the code below tries to be neat and reusable:
#
slash = os.path.sep
bundleDir = os.path.normpath(os.path.split(abcraft.__file__)[0]
                                + (slash + '..')*2 + slash)
# We 'know' (as in 'assume'!) that the packages containing suitable versoins 
# of certain tools reside alongsize the PARENT of the abcraft package:
#
abcraft.external.Abcm2svg.exe = (bundleDir + 'abcm2ps-6.6.22'
                                 + slash + 'abcm2ps.exe')
abcraft.external.Abc2midi.exe = (bundleDir + 'abcmidi-20150829'
                                 + slash + 'abc2midi.exe')

# only include this line if using a abc2midi vresion which gives line-col
# in error/warning mesages:
abcraft.external.Abc2midi.reMsg = r'.*in\s+line-char\s(\d+)\-(\d+).*'

print ("running abcraft.main")
abcraft.main()


