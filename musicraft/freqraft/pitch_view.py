# -*- coding: utf-8 -*-
"""
Various methods of drawing scrolling plots.
"""
import sys, os
import pyqtgraph as pg
from ..share import (dbg_print, QtCore, QtGui, Printer, image_dir)
import numpy as np
import math
import pyaudio
from PIL import Image
from .terpsichore import default_voice, Clef, Note
Signal = QtCore.Signal

SHOW_VOLUMES = 0
AUDIO_SAMPLE_RATE = 44100


class PitchPlot(pg.PlotItem):

    burst_signal = Signal(int, np.ndarray)

    fft_pen = (220, 220, 42) # bright yellow
    note_trace_pen = (128, 240, 128) # bright green?
    concertPitch=440.0
    pps = 1000  # points per semitone
    trace_scale = 0.005  # just a magic number 'for now'
    MIN_SAMPLES = AUDIO_SAMPLE_RATE * 0.02  # don't attempt to derive freq on less than 20 milliseconds

    def __init__(self):
        pg.PlotItem.__init__(self)
        self.setLabel('top', 'amplitude', '') # , pen=self.fft_pen)
        self.setLabel('bottom', 'Time', 's')
        self.setLabel('left', 'midi note', 'mst')

        self.setYRange(30*self.pps, 96*self.pps)
        self.setXRange(0, 2000)
        self.fft_curve = self.plot() # np.arange(1280), np.arange(1280))  # self.recent_samples)
        self.fft_curve.setPen(self.fft_pen)

        #self.recent_notes = np.array([60000]+[np.NaN]*10000)
        self.recent_notes = np.arange(2000) * 30.
        self.note_trace = self.plot(self.recent_notes, connect='finite')
        self.note_trace.setPen(self.note_trace_pen)
        self.draw_staves_etc()
        self.setPreferredSize(800, 600)
        self.it = 0
        self.burst_signal.connect(self.interpret_burst)

    def draw_staves_etc(self):
        all_staff_lines = []  # accumulator

        for clef in (Clef.Bass, Clef.Treble):
            all_staff_lines += clef.lines
            img = Image.open(image_dir + clef.symbol).resize(
                (32*clef.scaleHint, 900*clef.scaleHint), Image.ANTIALIAS)
            img_ar = np.array(img)
            img_ar_v = np.swapaxes(np.flipud(img_ar.view(dtype=np.uint32).reshape(img_ar.shape[:-1])), 0, 1)
            img_item = pg.ImageItem(img_ar_v, opacity=0.5)
            self.addItem(img_item, autoLevels=False)

            marked_semi = clef.lines[clef.marked]
            img_item.setPos(0, (marked_semi.GetPitch() - clef.descent)*self.pps)

        for ixPitch in range(128):
            note = default_voice.GetNote(ixPitch)
            width = 1
            style = None
            label = note.real_name
            labelOpts={'color': (200,0,0), 'movable': False, 'position': 0.8,
                       'anchors': (0.5, 0.5), 'fill': (0, 0, 200, 100)}
            if note in all_staff_lines:
                colour = (200, 200, 200)
                width = 2
            #elif note is Note.A4: # traditional tuning note nominally 440Hz but often inflated
            #    colour = (0, 200, 0)
            #elif note.pitch == 0:
            elif note is Note.C4:
                label += " = middle C"
                style = QtCore.Qt.DashLine
                colour = (220, 220, 220)
            elif len(note.real_name) == 2:
                colour = (200, 30, 30)
            else:
                colour = (150, 30, 30)
                label = None
            inf_line = pg.InfiniteLine(movable=False, angle=0, pos=ixPitch*self.pps,
                                       pen=dict(color=colour, width=width, style=style),
                                       # bounds = [-20, 20],
                                       # hoverPen=(0,240,0),
                                       ) #label=label, labelOpts=labelOpts)
            self.addItem(inf_line)

    def interpret_burst(self, quiets, samples, believe=True, minFreq=10, maxFreq=1024, spread=3,
                            transpose=False):
        nSamples = len(samples)
        # print ('interpret_burst', quiets, nSamples)
        if len(samples) < self.MIN_SAMPLES:
            quiets += len(samples)
            samples = samples[0:0]  # empty it but keep the type
            # print ("tiddler!")
        if len(samples):
            self.fftAmplitudes = np.array((abs(np.fft.fft(samples))/nSamples)[minFreq:maxFreq],
                                          dtype=np.int32)
            self.fftFrequencies = (AUDIO_SAMPLE_RATE*np.arange(nSamples))[minFreq:maxFreq]/(nSamples*1)
            indexMaxAmplitude = np.argmax(self.fftAmplitudes)
            amplitudes = self.fftAmplitudes[indexMaxAmplitude-spread:indexMaxAmplitude+spread+1]
            frequencies = self.fftFrequencies[indexMaxAmplitude-spread:indexMaxAmplitude+spread+1]
            total = np.sum(amplitudes)
            volume = math.log(total+1, 2.0)
            avgFrequency = np.sum(frequencies*amplitudes)/total
            absPitch = 1000 * (69 + 12 * math.log((avgFrequency / self.concertPitch), 2.0))
            # print("absPitch =", absPitch, 'mst')
            try:
                avgNote = default_voice.GetNote(absPitch / 1000., transpose=False)
            except (ValueError, IndexError):
                avgNote = np.NaN
                absPitch = None
            # print(avgNote)

            pitches = self.pps * (np.log2(self.fftFrequencies / self.concertPitch)*12+69)
            self.fft_curve.setData(self.fftAmplitudes * 10, pitches)
        else:
            avgNote = np.NaN
            absPitch = None
        l = int((quiets+len(samples)) * self.trace_scale)
        # absPitch = self.it * 1000.
        self.recent_notes[:-l] = self.recent_notes[l:]
        self.recent_notes[-l:] = np.array([absPitch or np.NaN]*l)
        self.note_trace.setData(self.recent_notes, connect='finite')
        self.update()
        self.show()


class PitchView(pg.GraphicsView):
    FRAMES_PER_BUFFER = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    INPUT_DEVICE_INDEX = 2 # None  # i.e use default
    MIN_SIG_VOLUME = 400
    MAX_BURST = AUDIO_SAMPLE_RATE * 0.2
    MAX_QUIETS = AUDIO_SAMPLE_RATE * 0.5

    update_signal = Signal(np.ndarray)

    one_shot_mode = False

    def __init__(self):
        pg.GraphicsView.__init__(self)
        self.setWindowTitle("Musicraft: Pitch and Note Plot")
        self.lay = pg.GraphicsLayout(border=(100, 100, 100))
        self.setCentralItem(self.lay)
        #raw_plot = self.lay.addPlot()
        raw_plot = pg.PlotItem()
        self.lay.addItem(raw_plot)
        raw_plot.setYRange(-1024, 1024)
        raw_plot.setMaximumSize(200., 200.)
        self.recent_samples = np.zeros(AUDIO_SAMPLE_RATE, dtype=np.int16)  # display one seconds worth of raw data
        self.raw_curve = raw_plot.plot(self.recent_samples)
        self.start_index = self.end_index = self.quiets = 0
        self.thresholds = [pg.InfiniteLine(pos=y, angle=0, pen=None, movable=True)
                           for y in (self.MIN_SIG_VOLUME, - self.MIN_SIG_VOLUME)]
        for is_other, th in enumerate(self.thresholds):
            raw_plot.addItem(th)
            th.sigPositionChanged.connect(self.threshold_changed)

        self.pitch_plot = PitchPlot()
        self.lay.addItem(self.pitch_plot, col=1, colspan=6)
        self.pitch_plot.setPreferredHeight(500.)

        self.init_audio()
        self.show()

    def threshold_changed(self, line):
        y = line.pos().y()
        for th in self.thresholds:
            if line is not th:
                th.setPos(-y)
        self.MIN_SIG_VOLUME = abs(y)


    def init_audio(self):
        self.update_signal.connect(self.accumulate)
        self.pyaud = pyaudio.PyAudio()
        self.stream = self.pyaud.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=AUDIO_SAMPLE_RATE,
            frames_per_buffer=self.FRAMES_PER_BUFFER,
            input_device_index=self.INPUT_DEVICE_INDEX,
            input=True,
            stream_callback = self.got_audio_block
        )
        return

    def got_audio_block(self, raw_bytes, frame_count, time_info, status):
        dbg_print(frame_count, time_info, status)
        self.update_signal.emit(np.fromstring(raw_bytes, dtype=np.int16))
        return raw_bytes, pyaudio.paContinue

    def accumulate(self, new_samples):
        dbg_print("accumulate", len(new_samples))
        if self.end_index:  # 'update_graphs' clears this except in one-shot mode!
            return

        self.recent_samples[:-self.FRAMES_PER_BUFFER] = self.recent_samples[self.FRAMES_PER_BUFFER:]
        self.recent_samples[-self.FRAMES_PER_BUFFER:] = new_samples
        abs_samples = abs(new_samples)
        i_max_volume = np.argmax(abs_samples)
        new_volume = abs_samples[i_max_volume]
        start_of_frame_index = len(self.recent_samples) - self.FRAMES_PER_BUFFER
        on = new_volume > self.MIN_SIG_VOLUME
        if self.start_index:  # in middle of burst (or blip)
            self.start_index -= len(new_samples)
            if not on:  # end of burst
                self.end_index = start_of_frame_index
                new_quiets = self.FRAMES_PER_BUFFER
            elif (start_of_frame_index - self.start_index) > self.MAX_BURST:
                self.end_index = len(self.recent_samples)
                new_quiets = 0
        else:  # was silent(ish) at last sample
            if on:
                self.start_index = start_of_frame_index
            else:
                self.quiets += self.FRAMES_PER_BUFFER
                if self.quiets >self.MAX_QUIETS:
                    self.start_index = self.end_index = len(self.recent_samples)
                    new_quiets = 0

        if self.end_index:  # i.e if any cause to alert the burst handler...
            self.pitch_plot.burst_signal.emit(self.quiets,
                                              self.recent_samples[self.start_index:self.end_index])
            self.quiets = new_quiets
            self.start_index = 0
            if not self.one_shot_mode:
                self.end_index = 0
        self.update_amplitude_graph()

    def update_amplitude_graph(self):
        self.raw_curve.setData(self.recent_samples)

if __name__ == '__main__':
    pg.mkQApp()
    apw = PitchView()
    apw.start()
## Start Qt event loop unless running in interactive mode or using pyside.
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
