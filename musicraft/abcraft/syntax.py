"""
This ABC syntax highlighter doesn't need to do much parsing; this is done by
'abcm2ps' and written into the '.svg' file. 'score.py' then constructs an easy to
use dictionary structure from this,
"""
#built using python highligher as starting point.

from ..share import (dbg_print, QtCore, QtGui, Share)

import sys


def format(color, style='', size=None):
    """Return a QtGui.QTextCharFormat with the given attributes.
    """
    _color = QtGui.QColor()
    _color.setNamedColor(color)

    _format = QtGui.QTextCharFormat()
    _format.setForeground(_color)
    if 'bold' in style:
        _format.setFontWeight(QtGui.QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)
    if size is not None:
        _format.setFontPointSize(size)
    return _format


# Syntax styles that can be shared by all languages
STYLES = {
    'default': format('blue'),
    'notename': format('black', 'bold'),
    'string':  format('cyan', 'italic'),
    'comment':  format('green', 'italic'),
    'header': format('red', 'italic'),
    'decorator': format('black', 'italic'),
    'command': format('black', 'italic'),
}


class AbcHighlighter (QtGui.QSyntaxHighlighter):
    """Syntax highlighter for the abc(plus) music description language.
    """
    # Python keywords
    def __init__(self, document, editor):
        QtGui.QSyntaxHighlighter.__init__(self, document)
        self.editor = editor

    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text.
        """

        # I seem to have acquiesced to abcm2ps's scheme of counting rows from 1:
        elts_on_cols_in_row = Share.abcRaft.score.getEltsOnRow(1+self.currentBlock().blockNumber())
        for key_ in STYLES.keys():
            STYLES[key_].setFontPointSize(self.editor.pointSizeF)
        span = len(text)
        if text[1:2]==':':
            style_name = "header"
        elif text[0:2] == '%%':
            style_name = "command"
        else:
            ix =0
            while ix < len(text):
                style_name = 'default'
                span = 1
                eltAbc, eltHead = elts_on_cols_in_row.get(ix, (None, None))
                if eltAbc is not None:
                    style_name = 'notename'
                elif text[ix]=='%':
                    style_name = 'comment'
                    span = len(text)-ix
                else:
                    for startChar, endChar, maybe_style_name in (
                        ('"', '"', 'string'),
                        ('[', ']', 'header'),
                        ('!', '!', 'decorator'),
                    ):
                        if text[ix]!=startChar:
                            continue
                        try:
                            jx = text[ix+1:].index(endChar)
                        except ValueError:
                            break
                        #  broken for now! if jx>2 and text[ix+2]==':':  # distinguish embedded commands from chords
                        style_name = maybe_style_name
                        span = jx + 2
                        break
                self.setFormat(ix, span, STYLES[style_name])
                ix += span
        self.setCurrentBlockState(0)

    snippets = {
        'V': ('V:', ' name="', '" sname="', '"\n',),  # new voice
        'Q': ('Q:1/4',),  # new tempo indication
        '12': ('[1 ', ' :| [2 ',),  # varied repeat ending coding
        'cr': ('!<(!', ' !<)!',),  # hairpin dynamic
        'di': ('!>(!', '!>)!',),  # hairpin dynamic
        'CR': ('"_cresc."',),
        'Cr': ('"^cresc."',),
        'MR': ('"_molto rit."',),
        'Mr': ('"^molto rit."',),
        'PR': ('"_poco rit."',),
        'Pr': ('"^poco rit."',),
        'SB': ('"_steady beat"',),
        'Sb': ('"^steady beat"',),
        'm': ('[M:', '2/', '4]',),  # mid-line time-sig change
        'tt': ('!tenuto!',),
        'tp': ('!teepee!',),
        'ac': ('!>!',),  # accent; '><TAB>' also works
        'ro': ('!///!',),  # roll/roffel; '///<TAB>' also works
        'st': ('!dot!',),  # staccato; 'dot<TAB>' also works
        '.': ('!dot!',),  # staccato; 'dot<TAB>' also works
        'gl': ('!-(!', '!-)!'),  # glissando
        'sd': ('[I:pos stem down]',),
        'su': ('[I:pos stem up]',),
        'sa': ('[I:pos stem auto]',),
    }

    def getSnippet(self, tc):    #------ Drag and drop
        col0 = col = tc.positionInBlock()
        block = tc.block()
        l = block.length()
        print("ABC get snippet", l)
        blockText = block.text()
        while col and ((col >= (l - 1))
                       or not (str(blockText[col - 1]) in ' |!]')):
            tc.deletePreviousChar()
            col -= 1
        key = blockText[col:col0]
        print("autoComplete key %d:%d '%s'" % (col, col0, key))
        return self.snippets.get(key, ("!%s!" % key,))

