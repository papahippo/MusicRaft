"""
MusicRaft
"""

#from distutils.core import setup
from setuptools import setup

setup(name = 'MusicRaft',
    version = '0.4.2',
    author = "Larry Myerscough",
    author_email='hippostech@gmail.com',
    packages=['musicraft', 'musicraft.abcraft', 'musicraft.freqraft', 'musicraft.pyraft', 'musicraft.playraft', 'musicraft.raft', 'musicraft.share', ],
    scripts=['bin/run_musicraft.py'],
    url='http://larry.myerscough.nl/terpsichore/musicraft.py',
    license='LICENSE.txt',
    description='GUI for abcplus music notation.',
    long_description=open('README.txt').read(),
    install_requires=[
        "numpy >= 1.1.1",
        "mido >= 1.1.1",
        "pyqtgraph >= 0.10.0",
# problematic!        "PySide >= 1.1.1",

    ],
)
