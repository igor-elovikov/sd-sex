import sys

from PySide2.QtCore import QRegExp
from PySide2.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat
from PySide2.QtWidgets import QApplication, QPlainTextEdit

import sexparser

def format(color, style=''):
    """Return a QTextCharFormat with the given attributes.
    """
    _color = QColor()
    _color.setNamedColor(color)

    _format = QTextCharFormat()
    _format.setForeground(_color)
    if 'bold' in style:
        _format.setFontWeight(QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)

    return _format

hl_colors = {
    'yellow': '#e5c07b',
    'blue': '#61afef',
    'magenta': '#c678d2',
    'gray': '#7f848b',
    'turq': '#56b6c2',
    'white': '#abb2bf',
    'orange': '#d19a61',
    'green': '#98c379',
    'rose': '#e06c75'
}

# Syntax styles that can be shared by all languages
STYLES = {
    'keyword': format(hl_colors['rose'], 'bold'),
    'operator': format(hl_colors['turq']),
    'function': format(hl_colors['blue']),
    'brace': format(hl_colors['white']),
    'string': format(hl_colors['yellow']),
    'string2': format(hl_colors['yellow']),
    'comment': format(hl_colors['gray'], 'italic'),
    'builtin_type': format(hl_colors['turq'], 'italic'),
    'builtin_constant': format(hl_colors['magenta']),
    'output': format(hl_colors['green'], 'bold'),
    'numbers': format(hl_colors['magenta']),
}

class SexHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for the Python language.
    """
    # Python keywords
    keywords = [
        'if', 'else', 'not', 'and', 'or', sexparser.export_function_name, sexparser.declare_inputs_function_name, 'for', 'in', 'endfor', 'endif', 'macro', 'endmacro', '::', '{{', '}}',
        'include', 'import', 'set', 'as', 'extend', 'return'
    ]

    builtin_constant = [
        'True', 'False', 
    ]

    # Python operators
    operators = [
        '=',
        # Comparison
        '==', '!=', '<', '<=', '>', '>=', 
        # Arithmetic
        r'\+', r'-', r'\*', r'/', r'//', r'\%', r'\*\*', r'\@', 
        # In-place
        r'\+=', r'-=', r'\*=', r'/=', r'\%=',
        # Bitwise
        r'\^', r'\|', r'\&', r'\~', '>>', '<<',
    ]

    # Python braces
    braces = [
        r'\{', r'\}', r'\(', r'\)', r'\[', r'\]',
    ]

    def __init__(self, document):
        QSyntaxHighlighter.__init__(self, document)
    
    def setup_rules(self, builtin_functions, builtin_types):

        rules = []

        # Keyword, operator, functions and brace rules
        rules += [(r'\b%s\b' % w, 0, STYLES['keyword'])
            for w in SexHighlighter.keywords]

        rules += [(r'\b%s\b' % w, 0, STYLES['function'])
            for w in builtin_functions]

        rules += [(r'\b%s\b' % w, 0, STYLES['builtin_constant'])
            for w in SexHighlighter.builtin_constant]

        rules += [(r'\b%s\b' % w, 0, STYLES['builtin_type'])
            for w in builtin_types]

        rules += [(r'\b%s\b' % sexparser.output_variable_name, 0, STYLES['output'])]

        rules += [(r'%s' % o, 0, STYLES['operator'])
            for o in SexHighlighter.operators]

        rules += [(r'%s' % b, 0, STYLES['brace'])
            for b in SexHighlighter.braces]

        

        # All other rules
        rules += [
            # Numeric literals
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, STYLES['numbers']),

            # From '#' until a newline
            (r'#[^\n]*', 0, STYLES['comment']),            

            # Double-quoted string, possibly containing escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
            # Single-quoted string, possibly containing escape sequences
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string']),
        ]

        # Build a QRegExp for each pattern
        self.rules = [(QRegExp(pat), index, fmt)
            for (pat, index, fmt) in rules]


    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text.
        """
        # Do other syntax formatting
        for expression, nth, format in self.rules:
            index = expression.indexIn(text, 0)

            while index >= 0:
                # We actually want the index of the nth match
                index = expression.pos(nth)
                length = len(expression.cap(nth))
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)
