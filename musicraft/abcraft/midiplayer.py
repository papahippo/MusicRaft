#!/usr/bin/env python
"""                                                                            
Play MIDI file on output port.

Run with (for example):

    ./play_midi_file.py 'SH-201 MIDI 1' 'test.mid'
"""

import sys, mido
from ..share import (Share, Signal, WithMenu, dbg_print, QtCore, QtGui)


class MidiPlayer(QtGui.QWidget):
        
    lineAndCol = Signal(int, int)

    outputPort = 'TiMidity port 0'

    def __init__(self):
        QtGui.QWidget.__init__(self)
        try:
            self.output = mido.open_output(self.outputPort)
        except IOError as exc:
            print ("sorry; couldn't setup MIDI player; exception details follow <<<")
            print (exc)
            print (">>>. Perhaps overruling outputPort (currently {0}) will help".format(self.outputPort))
            self.output = None
        dbg_print('MidiPlayer:__init__', self.output)

    def play(self, filename):
        self.output.reset()
        self.accum = dict([(i, 0) for i in range(110, 115)])
        self.midiFile = mido.MidiFile(filename)
        self.messages = self.midiFile.__iter__() # self.midiFile.play()
        self.pendingMessage = None
        self.paused = False
        self.cueMessage()

    def pause(self):
        self.paused = not self.paused
        self.cueMessage()

    def cueMessage(self):
        if self.paused:
            return
        message = self.pendingMessage
        self.pendingMessage = None
        while True:
            if message:
                if not isinstance(message, mido.MetaMessage):
                    if message.type == 'control_change':
                        self.accum[message.control] = message.value
                    else:
                        self.output.send(message)
                        lineNo = ((self.accum[110]<<14)
                                 +(self.accum[111]<<7)
                                 + self.accum[112])
                        colNo =  ((self.accum[113]<<7)
                                 + self.accum[114])
                        self.lineAndCol.emit(lineNo, colNo-1)
            try:
                message = next(self.messages)
            except StopIteration:
                dbg_print('cue_msg; StopIteration')
                return
            dbg_print(message.type, message)
            if message.time != 0:
                break
        self.pendingMessage = message
        milliseconds = int(message.time * 1000)
        QtCore.QTimer.singleShot(milliseconds, self.cueMessage)

    def __del__(self):
        dbg_print('MidiPlayer:__del__',)
        #self.output.reset()

if __name__ == '__main__':
    class MainWindow(QtGui.QMainWindow):
        def __init__(self):
            super(MainWindow, self).__init__()
    
            self.midiPlayer = MidiPlayer()
    
            fileMenu = QtGui.QMenu("&File", self)
            quitAction = fileMenu.addAction("E&xit")
            quitAction.setShortcut("Ctrl+Q")
    
            self.menuBar().addMenu(fileMenu)
    
    
            quitAction.triggered.connect(QtGui.qApp.quit)
    
            self.setCentralWidget(self.midiPlayer)
            self.setWindowTitle("MidiPlayer")
            self.midiPlayer.lineAndCol.connect(self.showLocation)
            self.midiPlayer.play(
                (len(sys.argv)>1 and sys.argv[1]) or './MarThruAm_timp.midi')
            #self.resize(self.view.sizeHint() + QtCore.QSize(
            #    80, 80 + self.menuBar().height()))

        def showLocation(self, lineNo, colNo):
            dbg_print('showLocation(line, col)', lineNo, colNo)

    app = QtGui.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
