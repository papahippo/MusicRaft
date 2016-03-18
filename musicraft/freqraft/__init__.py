#!/usr/bin/python
"""
Copyright 2015 Hippos Technical Systems BV.

@author: larry
"""
from __future__ import print_function
import sys
import numpy
import pyaudio
from ..share import (Share, dbg_print, QtCore, QtGui, Printer)
from ..raft.external import StdTab
from .terpsichore import default_voice
from .freq_view import FreqView


class FreqRaft(object):
    inputDeviceIndex = 0
    creMsg = reMsg = None  # to be reviewed - nec. for StdTab
    stdFont = 'Courier New', 10, False  # likewise!
    rowColOrigin = (0, -1)  # also likewise!

    def __init__(self):
        Share.pyRaft = self
# following code cribbed from source code of myPlot1.py:
        try:
            self.pyaud = pyaudio.PyAudio()
            self.stream = self.pyaud.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                #input_device_index=self.inputDeviceIndex,
                input=True,
                stream_callback=self.mic_callback)
            self.latest_note = "Valid input device but no note yet"
        except KeyError:
            print ("I cannot open pyaudio!\n", file=sys.stderr)
            self.stream = None

        self.freqView = FreqView()
        Share.raft.displayBook.addTab(self.freqView, "Tuning")
        self.stdTab = StdTab(self)
        Share.raft.stdBook.widget.addTab(self.stdTab,
                                     'frequency')

    def write(self, text):
        self.stdTab.setPlainText(str(text))

    def mic_callback(self, in_data, frame_count, time_info, status):
        # global data1, curve1
        # print (frame_count, hex(len(in_data)), file=sys.stderr)
        samples = numpy.fromstring(in_data, dtype=numpy.int16)

        avgNote, volume = default_voice.DeriveNote(samples)
        pitch = avgNote and avgNote.GetPitch()
        if pitch is not None and volume>6.:
            print("pitch=%s avgNote=%s volume=%s\n"
                 % (pitch,  avgNote,  volume))
            # data1[:-1] = data1[1:]  # shift data in the array one sample left
                                    # (see also: np.roll)
            # data1[-1] = pitch
            # curve1.setData(data1)

        return (in_data, pyaudio.paContinue)


