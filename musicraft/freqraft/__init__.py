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
        Share.freqRaft = self
# following code cribbed from source code of myPlot1.py:
        try:
            self.pyaud = pyaudio.PyAudio()
            self.stream = self.pyaud.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                frames_per_buffer=2000,
                #input_device_index=self.inputDeviceIndex,
                input=True)  # ,
                # stream_callback=self.mic_callback)
            self.latest_note = "Valid input device but no note yet"
        except KeyError:
            print ("I cannot open pyaudio!\n", file=sys.stderr)
            self.stream = None

        self.freqView = FreqView()
        Share.raft.displayBook.addTab(self.freqView, "Tuning")
        self.stdTab = StdTab(self)
        Share.raft.stdBook.widget.addTab(self.stdTab,
                                     'frequency')
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.timer_callback)
        self.timer.start(50)

    def write(self, text):
        self.stdTab.appendPlainText(str(text))
        #print(text)

    def timer_callback(self):
        # global data1, curve1
        # print (frame_count, hex(len(in_data)), file=sys.stderr)
        #print('timer_callback.1')
        in_data = self.stream.read(4000)
        samples = numpy.fromstring(in_data, dtype=numpy.int16)
        #print('timer_callback.2', len(in_data))
        avgNote, volume = default_voice.DeriveNote(samples)
        pitch = avgNote and avgNote.GetPitch()
        if volume>6.:
            if pitch is not None:
                self.write("pitch=%s avgNote=%s volume=%s\n"
                             % (pitch,  avgNote,  volume))
            # data1[:-1] = data1[1:]  # shift data in the array one sample left
                                    # (see also: np.roll)
            # data1[-1] = pitch
            # curve1.setData(data1)
            self.freqView.add_sample(volume, pitch)

        return (in_data, pyaudio.paContinue)

    if 0:
        def mic_callback(self, in_data, frame_count, time_info, status):
            # global data1, curve1
            # print (frame_count, hex(len(in_data)), file=sys.stderr)
            samples = numpy.fromstring(in_data, dtype=numpy.int16)

            avgNote, volume = default_voice.DeriveNote(samples)
            pitch = avgNote and avgNote.GetPitch()
            if pitch is not None and volume>6.:
                self.write("pitch=%s avgNote=%s volume=%s\n"
                     % (pitch,  avgNote,  volume))
                # data1[:-1] = data1[1:]  # shift data in the array one sample left
                                        # (see also: np.roll)
                # data1[-1] = pitch
                # curve1.setData(data1)

            return (in_data, pyaudio.paContinue)


