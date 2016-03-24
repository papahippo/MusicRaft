#!/usr/bin/python
"""
# terpsichore - another object oriented approach to music representation in the python language.
#    The defining feature of 'terpsichore' iis that notes are represented not as quoted strings
#    but as instances of a 'note' class.
# N.B. This has been hacked rather impatiently/unsympathetically in order to use it within
#    'musicraft'.
"""
import numpy, math
# import analyse

all_Keys = {}
note_letters = ('C', None, 'D', None, 'E', 'F', None, 'G', None, 'A', None, 'B')

notes_by_Pitch = numpy.array([[None,None]]*128)

class musicGroup(object):
    pass

class musicItem(object):
    pass

class Note_(musicItem):

    def __init__(self, frequency=None, pitch=None, octave=None, length=None, instrument=None, real_name=None):
        if frequency is not None:
            aPitch = 69 + 12 * math.log((frequency / 440.0), 2.0)
            octave = int(aPitch/12)-1
            pitch = aPitch - 12*(octave+1)
            print (aPitch, pitch, octave)
        self.pitch = pitch
        self.octave = octave
        self.length = length
        self.real_name = real_name

    def __repr__(self):
        return "Note:'%s' (pitch=%g)"%(self.real_name, self.GetPitch())

    def GetPitch(self, octave=None):
        
        octave = octave or self.octave
        if octave is None:
            return None
        return (octave+1)*12+self.pitch
    
class Note(musicGroup):
    pass

AllNotes = {}

class _Mode(musicItem):
    def __init__(self, isMinor, suffix, full_name):
        self.isMinor = isMinor
        self.suffix = suffix
        self.full_name = full_name

    def __repr__(self):
        return "Mode:'%s' (suffix=%s)"%(self.full_name, self.suffix)

class Mode:
    Major = _Mode(False, 'M', 'Major')
    Minor = _Mode(True, 'm', 'Minor')

class _Key(object):
    # not fully thought out yet!
    def __init__(self, fifths, mode, real_name):
        self.fifths = fifths
        self.real_name = real_name
        self.mode = mode

    def __repr__(self):
        return "Key:'%s' (fifths=%d)\n" %(self.real_name, self.fifths)

class Key(musicGroup):
    pass

for octave in [None]+list(range(-1,10)):
    #print ("------- octave........", octave)
    for pitch, letter in enumerate(note_letters):
        if not letter:
            continue
        if octave is None:
            octave_suffix = ''
        else:
            octave_suffix = '%d' %octave
        for delta, accidental in ((-2, 'bb'), (-1, 'b'), (0, ''), (1, '#'), (2, 'x')):
            real_name = letter+accidental+octave_suffix
            python_name = real_name.replace('#', 'i')
            stepped_pitch = pitch+delta
            new_note = Note_(pitch=stepped_pitch, octave=octave, real_name=real_name)
            #print ('new_note', "=", new_note)
            new_Pitch = new_note.GetPitch()
            if (new_Pitch is not None) and (new_Pitch<0 or new_Pitch>=128):
                continue
            setattr(Note, python_name, new_note)
            AllNotes[new_Pitch] = new_note
            #print ("new_Pitch =", new_Pitch)
            if delta in (2, -2):
                continue
            for i_sharp_flat in (0,1):
                if octave is None:
                    # convenient to hang the key creation stuff in here:
                    for mode in (Mode.Major, Mode.Minor):
                        python_key_name = python_name+mode.suffix
                        if python_key_name in all_Keys:
                            continue
                        real_key_name = real_name+mode.suffix
                        if mode.isMinor:
                            fifths = stepped_pitch+3
                        else:
                            fifths = stepped_pitch
                        if fifths & 1:
                            fifths = fifths+6
                        fifths = ((fifths+6)%12)-6
                        if (not i_sharp_flat) and (fifths<0):
                            fifths += 12
                        elif i_sharp_flat and (fifths>0):
                            fifths -= 12
                        setattr(Key, python_key_name, _Key(fifths, mode, real_key_name))
                elif (2*i_sharp_flat != (1+delta) and
                          (notes_by_Pitch[new_Pitch][i_sharp_flat] is None
                        or len(notes_by_Pitch[new_Pitch][i_sharp_flat].real_name) > 2)):
                    notes_by_Pitch[new_Pitch][i_sharp_flat] = new_note

class _Clef(musicItem):
    def __init__(self, lines=[], marked=None, symbol=None, scaleHint=16, descent=7):
        self.lines = lines
        self.marked = marked
        self.symbol = symbol
        self.scaleHint = scaleHint
        self.descent = descent

class Clef(musicGroup):
    Treble = _Clef(lines=(Note.E4, Note.G4, Note.B4, Note.D5, Note.F5),
                   descent=5, marked=1, symbol='Treble_clef_inv.png', scaleHint=16)
    Bass   = _Clef(lines=(Note.G2, Note.B2, Note.D3, Note.F3, Note.A3),
                   descent=8.5, marked=3, symbol='Bass_clef_inv.png', scaleHint=13)

class Voice(musicItem):
    def __init__(self, pitch_shift=0, clef=None, key=Key.CM, default_octave=3,
                    length=None, instrument=None, name=None):
        self.pitch_shift = pitch_shift
        self.clef = clef
        self.key = key
        self.default_octave = default_octave
        self.instrument = instrument
        self.name = name

    def __repr__(self):
        return "voice:'%s' (pitch_shift=%u)" %(self.name, self.pitch_shift)

    def GetPitch(self, wild, transpose=False):
        if isinstance(wild, (tuple, list, numpy.ndarray)):
            #print("list or tuple!")
            return [self.GetPitch(item, transpose) for item in wild]
        elif isinstance(wild, Note_):
            #print("note!")
            wild = wild.GetPitch()
            if transpose:
                wild -= self.pitch_shift
        return wild  # number, presumably!

    def GetNote(self, note_or_number, transpose=False):
        if isinstance(note_or_number, Note_):
            return note_or_number # note, thus
        elif isinstance(note_or_number, int):
            return notes_by_Pitch[note_or_number][self.key.fifths <= 0]
        elif isinstance(note_or_number, float):
            #return notes_by_Pitch[int(note_or_number)][self.key.fifths<0]
            i_near = int(note_or_number+0.5)
            #return str(i_near)
            note_near = notes_by_Pitch[i_near][self.key.fifths<0]
            miss = note_or_number - i_near
            if miss > 0.1:
                s_miss = '+'
            elif miss < -0.1:
                s_miss = '-'
            else:
                s_miss = '='
            return Note_(octave=note_near.octave, pitch=note_near.pitch+miss,
                        real_name=note_near.real_name+s_miss)

    #def DeriveNote(self, samples, sampleRate=44100, minFreq=10, maxFreq=2000, spread=3,         
    def DeriveNote(self, samples, sampleRate=44100, minFreq=10, maxFreq=400, spread=3,         
                            transpose=False, concertPitch=440.0):
            nSamples = len(samples)
            fftAmplitudes = (abs(numpy.fft.fft(samples))/nSamples)[minFreq:maxFreq]
            fftFrequencies = (sampleRate*numpy.arange(nSamples))[minFreq:maxFreq]/(nSamples*1)
            indexMaxAmplitude = numpy.argmax(fftAmplitudes)
            fftAmplitudes = fftAmplitudes[indexMaxAmplitude-spread:indexMaxAmplitude+spread+1]
            fftFrequencies = fftFrequencies[indexMaxAmplitude-spread:indexMaxAmplitude+spread+1]
            total = numpy.sum(fftAmplitudes)
            #print ("total", total)
            volume = math.log(total+1, 2.0)
            avgFrequency = numpy.sum(fftFrequencies*fftAmplitudes)/total
            absPitch = 69 + 12 * math.log((avgFrequency / concertPitch), 2.0)
            # print  ("absPitch =", absPitch)
            try:
                avgNote = self.GetNote(absPitch, transpose=transpose)
            except:
                avgNote = None
            return avgNote, volume
        
current_voice = default_voice = Voice()

class _Instrument(musicItem):
    """ distinction between instrument and voice rather iffy at present!
    """
    def __init__(self, clef=Clef.Treble, strings=None, real_name=None):
        self.strings = strings
        self.real_name = real_name
        self.clef = clef

    def __repr__(self):
        s = self.strings and "(%s strings)" %len(self.strings) or ""
        return "instrument:'%s'%s" %(self.real_name,s)
class Instrument(musicGroup):
    pass

def add_Instrument(real_name='ANInstrumment', python_name=None, clef=Clef.Treble, strings=None):
    if not python_name:
        python_name = real_name.replace(' ', '_').replace('#', 'i')
    setattr(Instrument, python_name, _Instrument(real_name=real_name, clef=clef, strings=strings))
    
def isInstrument(entity):
    return isinstance(entity, _Instrument)

add_Instrument('Guitar', strings=(Note.E2, Note.A2, Note.D3, Note.G3, Note.B3, Note.E4))
add_Instrument('Violin', strings=(Note.G3, Note.D4, Note.A4, Note.E5))
add_Instrument('Viola',  strings=(Note.C3, Note.G3, Note.D4, Note.A4))
add_Instrument('Chello', strings=(Note.C2, Note.G2, Note.D3, Note.A3))

# following two 'instruments' are dubious but handy at this stage of development:

add_Instrument('Treble Voice')
add_Instrument('Bass Voice', clef=Clef.Bass)

current_instrument = Instrument.Guitar

# quick hack for use by fortuna440

def best_note_name_for_pitch(i):
    nbp = notes_by_Pitch[i]
    return min ([n.real_name for n in nbp if not '#' in n.real_name])
#print(Instrument.__dict__.values())

if __name__ == '__main__':
    #print (Note.A3, Note.B4, [(notes_by_Pitch[i],'\n') for i in range(56,62)])
    print ([best_note_name_for_pitch(i) for i in range(50,70)])
    clef =Clef.Bass
    marked_semi = clef.lines[clef.marked]
    print(marked_semi, marked_semi.GetPitch() - clef.descent)  #, dir(marked_semi))
