# 'abcraft' is the git PROJECT title of this tree of files containing the
 python PACKAGE 'musicraft'.

'musicraft' started out as a rework of the geanypy plug-in 'ABCcraft'.

I reluctantly ditched the geanypy approach; gerany+geanypy is a great
editor+plug-in tool, but installation on a Windows system still seems to
require some good luck and/or black magic.

I have (somewhat belatedly!) radically separated the pure editing stuff
from the music-score related stuff.

Here is a quick synopsis of the musicraft package:

musicraft/__init__.py:
    This is the file which makes musicraft into a package.


I'm also maintaining two older prototype packages here:

abcraft-0.1 depends on the use of abcm2ps version 6.6.22. It has little or no
functionality not available in later versions so will be removed soon.

abcraft-0.2 works with most versions of abcm2ps, sometimes requiring tweaks in
the startup file. Until 'musicraft' is fully working, this is teh latest functional
version.


