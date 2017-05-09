"""
This ABC syntax highlighter doesn't need to do much parsing; this is done by
'abcm2ps' and written into the '.svg' file. 'score.py' then constructs an easy to
use dictionary structure from this,
"""
#built using python highligher as starting point.

from ..share import (dbg_print, QtCore, QtGui, Share)

import sys


def format(color, style=''):
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

    return _format


# Syntax styles that can be shared by all languages
STYLES = {
    'default': format('blue'),
    'notename': format('black', 'bold'),
}


class AbcHighlighter (QtGui.QSyntaxHighlighter):
    """Syntax highlighter for the abc(plus) music description language.
    """
    # Python keywords
    def __init__(self, document):
        QtGui.QSyntaxHighlighter.__init__(self, document)

    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text.
        """
        # I seem to have acquiesced to abcm2ps's scheme of counting rows from 1:
        elts_on_cols_in_row = Share.abcRaft.score.getEltsOnRow(1+self.currentBlock().blockNumber())
        for ix in range(len(text)):
            style_name = 'default'
            eltAbc, eltHead = elts_on_cols_in_row.get(ix, (None, None))
            if eltAbc is not None:
                style_name = 'notename'
            self.setFormat(ix, 1, STYLES[style_name])
        self.setCurrentBlockState(0)


