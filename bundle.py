#!/usr/bin/python
"""
Copyright 2015 Hippos Technical Systems BV.

@author: larry
"""
from __future__ import print_function
import sys, os, zipfile, webbrowser, pip

print ("aha")
class Bundle(object):
    target_package = '<must override!>'
    needs = ()          # default = needs nothing else but python!
    runners = {}       # default = target name = runner name


    def install(self):
        print ('sys.argv =', sys.argv)
        for package, url in self.needs:
            print ("'%s' needs package '%s'..."
                % (self.target_package, package))

            # windows installation of certain modules via 'pip' tends
            # to fail if certain MSVC assets are not present...
            # ... so we avoid using it. These cases are identified by
            # specifiying a (non None) an installation url in 'needs':
            #
            if sys.platform != 'win32' or  url is None:
                # easy-peasy thanks to 'pip'
                pip.main(['install', package])
            else:
                while True:
                    try:
                        __import__(package)
                        break # quit loop if package is already there...
                    except ImportError:
                        pass # ... otherwise stay in loop.
                    print ("Package '%s' cannot reliably be installed"
                            "via 'pip' under windows" % package)
                    print ( "... so I will browse to the binary installer.")
                    webbrowser.open(url)
                    print ("Save and execute '%s' in order to install '%s':"
                            % (os.path.split(url)[1], package))
                    raw_input("When you have done that, press the ENTER key here: ")
                print ("'%s' is ok!" % package)

        archiveFileName = sys.argv[0]
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

        runner_cmd = self.runners.get(sys.platform, "%s.py"
                                            % sys.platform)
        runner_dir = bare # os.getcwd() + os.path.sep + bare

        runner_filename = runner_dir + os.path.sep + runner_cmd
        if not os.path.exists(runner_filename):
            print ("warning: platform '%s' is not officially supported,"
                   " or at least not tested:" % sys.platform)
            print ("I will create a simplistic '%s'"
                    % runner_cmd)
            print ("This may well need to be 'tweaked' (edited)"
                   " to get it working!")
            with open(runner_filename, 'w') as new_script:
                new_script.write('import %s\n' % self.target_package)
                new_script.write('%s.main()\n' % self.target_package)

        print ("'%s' has been installed locally! in order to run it,"
                " go into directory %s (e.g. by the command 'cd %s')"
                " and enter the command:"
                %(self.target_package, runner_dir, bare))
        print("python %s" % runner_cmd)

        if sys.platform=='win32':
            pythonExe = "C:\Python27\python.exe"
            print ("depending on how you installed python, you may need"
                   "to use the long-hand command:\n"
                    "%s\\python %s" % (pythonExe, runner_cmd))

