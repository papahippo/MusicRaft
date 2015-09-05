#!/usr/bin/python
"""
Copyright 2015 Hippos Technical Systems BV.

@author: larry
"""
from __future__ import print_function
import sys, os, zipfile, webbrowser, pip

target_package = 'abccraft'

for package, url in (
    ('PySide', None),
    ('lxml', None),
    ('numpy', "http://sourceforge.net/projects/numpy/files/NumPy/1.7.0/"
              "numpy-1.7.0-win32-superpack-python2.7.exe"),
):
    print ("'%s' needs package '%s'..." % (target_package, package))

# windows installation of 'numpy' via 'pip' tends to fail if certain MSVC
# assets are not present, so we avoid using it.
#
    if sys.platform != 'win32' or  url is None:
        # easy-peasy thanks to 'pip'
        pip.main(['install', package])
    else:
        while True:
            try:
                __import__(package)
                break
            except ImportError:
                pass # i.e only do rest and stay in loop if module is missing!
            print ("Package '%s' cannot reliably be installed"
                    "via 'pip' under windows" % package)
            print ( "... so I will browse to the binary installer.")
            webbrowser.open(url)
            print ("Save and execute '%s' in order to install '%s':"
                    % (os.path.split(url)[1], package))
            raw_input("When you have done that, press the ENTER key here: ")
    print ("'%s' is ok!" % package)

archiveFileName = sys.path[0]
print (archiveFileName, os.getcwd())
bare, ext = os.path.splitext(archiveFileName)
if ext != '.pyz':
    print ("warning: this __main__ does not seem to be part of a '.pyz' file!")
    print ("if you have already installed '%s', you don't need to run"
            " '__main.py__' again.")
else:
    zf = zipfile.ZipFile(archiveFileName)
    # print (zf.namelist())
    zf.extractall() # members=['abcraft_etc/']) ... only does directory itself!

target_cmd = "%s.py" % sys.platform
target_dir = os.getcwd()+os.path.sep+target_package

if not os.path.exists(target_dir++os.path.sep+target_cmd):
    print ("warning: platform '%s' is not supported, or at least not tested:"
            % sys.platform)
    print ("perhaps you can create a working '%s' based on the existing files"
            % target_cmd)

print ("'%s' has been installed locally! in order to run it,"
        "  go into directory %s and enter the command:"
        %(target_package, target_dir))
print("%s" % target_cmd)

if sys.platfrom=='win32':
    pythonExe = "C:\Python27\python.exe"
    print ("depending on how you installed python, you may need to put\n"
            "%s infron tof teh above command" %  pythonExe  )
    target_cmd = 'win.py'
